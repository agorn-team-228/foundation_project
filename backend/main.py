from __future__ import annotations
import hashlib, json, re
from pathlib import Path
from contextlib import asynccontextmanager
import httpx
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import solution as core

STATE = {}

def clean_name(fn):
    return Path(fn).stem.replace("_", " ").replace("/", " ").strip()

def doc_id(name):
    return hashlib.md5(name.encode("utf-8")).hexdigest()[:10]

def meta(text):
    m = re.search(r"\b(\d{2}\.\d{2}\.\d{4})\b", text)
    date = m.group(1) if m else ""
    ed = "Действующая редакция"
    if re.search(r"утратил[аи]?\s+силу", text, re.I):
        ed = "Утратила силу"
    else:
        m2 = re.search(r"[Рр]едакция\s+от\s+(\d{2}\.\d{2}\.\d{4})", text)
        if m2:
            ed = "Редакция от " + m2.group(1)
    return date, ed

@asynccontextmanager
async def lifespan(app):
    kb = core.find_file("kb.zip", "knowledge-base.zip", "knowledge_base.zip")
    docs = core.load_documents(kb)
    parents, children = core.build_chunks(docs)
    index = core.build_hybrid_index(parents, children)
    reg, by_name = {}, {}
    for fn, text in docs:
        name = clean_name(fn)
        did = doc_id(name)
        date, ed = meta(text)
        sections = []
        for crumb, body in core._kb_sections(text):
            sections.append({"header": (name + " > " + crumb) if crumb else name, "text": body})
        if not sections:
            sections = [{"header": name, "text": text}]
        reg[did] = {"id": did, "doc_name": name, "title": fn, "date": date, "edition": ed, "sections": sections}
        by_name[name] = did
    STATE["index"] = index
    STATE["docs"] = reg
    STATE["by_name"] = by_name
    print("[startup] документов:", len(reg), "чанков:", len(children), flush=True)
    yield

app = FastAPI(title="Pravo API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ChatRequest(BaseModel):
    message: str
    history: list = []

FMT = ("Ты форматтер. Дан готовый юридический ответ. Разложи его в JSON, НЕ добавляя новых фактов. "
       "Поля: verdict (главный вывод до 20 слов), intro (остальной текст), "
       "steps (массив {title,text} только если в ответе есть перечисление действий, иначе []), "
       "prompt (один уточняющий вопрос или пустая строка). Верни ТОЛЬКО JSON.")

def fallback_format(answer):
    parts = re.split(r"(?<=[.!?])\s+", answer.strip(), maxsplit=1)
    return {"verdict": parts[0][:200], "intro": parts[1] if len(parts) > 1 else "", "steps": [], "prompt": ""}

def format_answer(client, answer):
    payload = {"model": core.LLM_MODEL, "temperature": 0.0, "max_tokens": 1500,
               "messages": [{"role": "system", "content": FMT}, {"role": "user", "content": answer}]}
    try:
        res = core.post_with_retry(client, "/chat/completions", core.LLM_KEY, payload, retries=2)
        txt = res["choices"][0]["message"].get("content", "") or ""
        m = re.search(r"\{.*\}", txt, re.DOTALL)
        if m:
            o = json.loads(m.group(0))
            steps = []
            for s in (o.get("steps") or []):
                if isinstance(s, dict) and s.get("text"):
                    steps.append({"num": len(steps) + 1, "title": str(s.get("title", ""))[:80], "text": str(s["text"])})
            return {"verdict": str(o.get("verdict") or "")[:250] or fallback_format(answer)["verdict"],
                    "intro": str(o.get("intro") or ""), "steps": steps, "prompt": str(o.get("prompt") or "")}
    except Exception as e:
        print("[format] fallback:", type(e).__name__, flush=True)
    return fallback_format(answer)

@app.get("/api/health")
def health():
    i = STATE.get("index")
    return {"status": "ok", "documents": len(STATE.get("docs", {})),
            "chunks": len(i.children) if i else 0,
            "vector_search": bool(i and i.faiss_index is not None)}

@app.get("/api/documents/{did}")
def get_doc(did: str):
    d = STATE.get("docs", {}).get(did)
    if not d:
        raise HTTPException(404, "Документ не найден")
    return d

@app.post("/api/chat")
def chat(req: ChatRequest):
    msg = (req.message or "").strip()
    if not msg:
        raise HTTPException(400, "Пустой вопрос")
    q = msg
    if req.history:
        lines = []
        for m in req.history[-6:]:
            role = "Пользователь" if m.get("sender") == "user" else "Ассистент"
            t = m.get("text") or m.get("verdict") or ""
            if t:
                lines.append(role + ": " + t)
        lines.append("Пользователь: " + msg)
        q = "\n".join(lines)
    with httpx.Client(timeout=180.0) as client:
        chunks = core.retrieve_context(client, q, STATE["index"])
        answer = core.generate_answer(client, q, chunks)
        out = format_answer(client, answer)
    sources, seen = [], set()
    for ch in chunks:
        did = STATE["by_name"].get(ch.doc_name)
        key = (did, ch.header)
        if did and key not in seen:
            seen.add(key)
            tail = ch.header.split(">")[-1].strip()
            label = (ch.doc_name + ", " + tail) if tail and tail != ch.doc_name else ch.doc_name
            sources.append({"docId": did, "header": ch.header, "label": label})
    out["sources"] = sources
    out["answer"] = answer
    return out
