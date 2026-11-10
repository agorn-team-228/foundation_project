import os
import json
import shutil
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session

from app.config import settings
from app.services.rag_service import RAGService
from app.services.ai_service import AIService

# --- Инициализация БД SQLite ---
os.makedirs("./data/documents", exist_ok=True)
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ORM Модели данных ---
class Chat(Base):
    __tablename__ = "chats"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, default="Новый диалог")
    category = Column(String, default="Жилищные вопросы")
    created_at = Column(DateTime, default=datetime.utcnow)
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, ForeignKey("chats.id"))
    sender = Column(String)
    text = Column(Text, nullable=True)
    structured_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    chat = relationship("Chat", back_populates="messages")

Base.metadata.create_all(bind=engine)

# --- Pydantic Схемы Валидации ---
class ChatCreate(BaseModel):
    id: str
    title: Optional[str] = "Новый диалог"
    category: Optional[str] = "Жилищные вопросы"

class ChatResponse(BaseModel):
    id: str
    title: str
    category: str
    created_at: datetime
    class Config: from_attributes = True

class MessageResponse(BaseModel):
    id: int
    sender: str
    text: Optional[str] = None
    structured_data: Optional[str] = None
    created_at: datetime
    class Config: from_attributes = True

class PromptRequest(BaseModel):
    message: str

# --- Инициализация FastAPI и Сервисов ---
app = FastAPI(title="Право AI Core")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_service = RAGService()
ai_service = AIService()

# --- Эндпоинты ---
@app.post("/api/chats", response_model=ChatResponse)
def create_chat(chat_data: ChatCreate, db: Session = Depends(get_db)):
    existing_chat = db.query(Chat).filter(Chat.id == chat_data.id).first()
    if existing_chat:
        return existing_chat
    new_chat = Chat(id=chat_data.id, title=chat_data.title, category=chat_data.category)
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat

@app.get("/api/chats", response_model=List[ChatResponse])
def list_chats(db: Session = Depends(get_db)):
    return db.query(Chat).order_by(Chat.created_at.desc()).all()

@app.get("/api/chats/{chat_id}/messages", response_model=List[MessageResponse])
def get_messages(chat_id: str, db: Session = Depends(get_db)):
    return db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at.asc()).all()

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    allowed_exts = [".txt", ".pdf", ".docx"]
    ext = os.path.splitext(file.filename).lower()
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail="Разрешены только: .txt, .pdf, .docx")
    
    file_path = f"./data/documents/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        rag_service.index_document(file_path)
        return {"status": "success", "detail": f"Документ {file.filename} успешно добавлен в базу RAG."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}")

@app.post("/api/chats/{chat_id}/prompt")
async def process_prompt(chat_id: str, payload: PromptRequest, db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    user_msg = Message(chat_id=chat_id, sender="user", text=payload.message)
    db.add(user_msg)
    
    context = rag_service.search_context(payload.message)
    try:
        ai_json_raw = await ai_service.generate_response(payload.message, context)
        if chat.title == "Новый диалог":
            chat.title = payload.message[:35] + "..."
            db.add(chat)
        ai_msg = Message(chat_id=chat_id, sender="ai", structured_data=ai_json_raw)
        db.add(ai_msg)
        db.commit()
        return json.loads(ai_json_raw)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка нейросети: {str(e)}")
