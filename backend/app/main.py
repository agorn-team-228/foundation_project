import os
import uuid
import json
import shutil
from datetime import datetime
from typing import List, Optional

# FastAPI & Pydantic
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# SQLAlchemy (Database)
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session

# PDF & DOCX Parsing
from pypdf import PdfReader
from docx import Document as DocxDocument

# LangChain & Text Splitting
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

# Vector Store
import chromadb

# OpenAI SDK for DeepSeek Integration
from openai import OpenAI

# ---------------------------------------------------------
# 1. КОНФИГУРАЦИЯ И ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ (SQLite)
# ---------------------------------------------------------
DATABASE_URL = "sqlite:///./legal_assistant.db"

# Создаем необходимые директории для документов и векторной базы данных
os.makedirs("./data/documents", exist_ok=True)
os.makedirs("./data/chroma_db", exist_ok=True)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------
# 2. SQLALCHEMY МОДЕЛИ ДАННЫХ (ORM)
# ---------------------------------------------------------
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
    sender = Column(String)  # 'user' или 'ai'
    text = Column(Text, nullable=True)
    structured_data = Column(Text, nullable=True)  # Хранение JSON-ответа AI в виде текста
    created_at = Column(DateTime, default=datetime.utcnow)

    chat = relationship("Chat", back_populates="messages")

# Инициализируем таблицы в локальной SQLite
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------
# 3. PYDANTIC СХЕМЫ ДЛЯ ВАЛИДАЦИИ API
# ---------------------------------------------------------
class ChatCreate(BaseModel):
    id: str
    title: Optional[str] = "Новый диалог"
    category: Optional[str] = "Жилищные вопросы"

class ChatResponse(BaseModel):
    id: str
    title: str
    category: str
    created_at: datetime
    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: int
    sender: str
    text: Optional[str] = None
    structured_data: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

class PromptRequest(BaseModel):
    message: str

# ---------------------------------------------------------
# 4. СЕРВИС RAG (Парсинг документов и поиск в ChromaDB)
# ---------------------------------------------------------
class RAGService:
    def __init__(self):
        # Подключаем локальное персистентное векторное хранилище
        self.chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(name="laws_collection")
        
        # Настраиваем инструмент деления текстов законов на смысловые фрагменты
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)

    def extract_text(self, file_path: str) -> str:
        """Извлекает текст в зависимости от расширения файла (.txt, .pdf, .docx)"""
        ext = os.path.splitext(file_path)[1].lower()  # исправлено: добавлен [1]
        text = ""
        
        if ext == ".pdf":
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() or ""
        elif ext == ".docx":
            doc = DocxDocument(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
                
        return text

    def index_document(self, file_path: str):
        """Разбивает документ на куски и индексирует их в векторную базу"""
        raw_text = self.extract_text(file_path)
        if not raw_text.strip():
            return
            
        chunks = self.text_splitter.split_text(raw_text)
        
        if chunks:
            ids = [str(uuid.uuid4()) for _ in chunks]
            metadatas = [{"source": os.path.basename(file_path)} for _ in chunks]
            
            # Локальная ChromaDB автоматически преобразует куски текста в эмбеддинги
            self.collection.add(documents=chunks, ids=ids, metadatas=metadatas)

    def search_context(self, query: str, n_results: int = 3) -> str:
        """Поиск релевантных нормативных актов под запрос пользователя"""
        results = self.collection.query(query_texts=[query], n_results=n_results)
        documents = results.get("documents", [])
        
        if documents and len(documents) > 0 and len(documents[0]) > 0:
            return "\n\n---\n\n".join(documents[0])
        return "Вгруженная законодательная база не содержит информации по данному запросу."

# ---------------------------------------------------------
# 5. AI СЕРВИС ИНТЕГРАЦИИ DEEPSEEK
# ---------------------------------------------------------
class AIService:
    def __init__(self):
        # DeepSeek API совместим с OpenAI SDK, передаем параметры через переменные окружения
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY", "mock-deepseek-key"),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://deepseek.com")
        )

    async def generate_response(self, user_question: str, context: str) -> str:
        system_prompt = (
            "Ты — профессиональный юридический AI-ассистент 'Право'.\n"
            "Твоя задача — отвечать на вопросы пользователя, опираясь СТРОГО на предоставленный контекст законодательства.\n"
            "КРИТИЧЕСКИЕ ПРАВИЛА:\n"
            "1. Отвечай только на основе предоставленного контекста. Тебе строго запрещено выдумывать статьи или ссылаться на несуществующие нормативные акты.\n"
            "2. Если в контексте нет прямого ответа на вопрос, верни JSON, где в поле 'verdict' будет написано 'Информации в базе данных недостаточно для формирования правового заключения'.\n"
            "3. Твой ответ должен быть СТРОГО валидным JSON-объектом. Не пиши никаких дополнительных слов, markdown-тегов вроде ```json или вступлений. Только чистый JSON со следующей структурой:\n"
            "   - 'verdict': Главный короткий правовой вывод ситуации (до 25 слов).\n"
            "   - 'intro': Развернутое введение со ссылками на законы из контекста.\n"
            "   - 'steps': Массив шагов решения проблемы (список объектов [{ 'num': 1, 'title': 'Заголовок', 'text': 'Действие' }]).\n"
            "   - 'prompt': Один уточняющий вопрос пользователю для конкретизации деталей."
        )

        user_content = f"ИНФОРМАЦИЯ ИЗ ВГРУЖЕННЫХ ЗАКОНОВ:\n{context}\n\nВОПРОС КЛИЕНТА:\n{user_question}"

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.0,  # Нулевая температура гарантирует отсутствие фантазий модели
            response_format={"type": "json_object"}
        )

        return response.choices[0].message.content  # исправлено: добавлен [0]

# Глобальные инстансы сервисов
rag_service = RAGService()
ai_service = AIService()

# ---------------------------------------------------------
# 6. FASTAPI МАРШРУТЫ И ЭНДПОИНТЫ
# ---------------------------------------------------------
app = FastAPI(title="Право AI Core API")

# Настройка CORS полиси
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Управление сессиями (чатами) ---

@app.post("/api/chats", response_model=ChatResponse)
def create_chat(chat_data: ChatCreate, db: Session = Depends(get_db)):
    """Создает новую сессию чата или возвращает существующую"""
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
    """Возвращает историю всех сессий для вывода в сайдбаре"""
    return db.query(Chat).order_by(Chat.created_at.desc()).all()

@app.get("/api/chats/{chat_id}/messages", response_model=List[MessageResponse])
def get_messages(chat_id: str, db: Session = Depends(get_db)):
    """Возвращает историю сообщений выбранной сессии"""
    return db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at.asc()).all()

# --- Динамическая загрузка и индексация документов ---

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Принимает, сохраняет на диск и индексирует файлы .txt, .pdf, .docx в ChromaDB"""
    allowed_exts = [".txt", ".pdf", ".docx"]
    ext = os.path.splitext(file.filename)[1].lower()  # исправлено: добавлен [1]

    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail="Формат файла не поддерживается. Разрешены только: .txt, .pdf, .docx"
        )
    
    file_path = f"./data/documents/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        rag_service.index_document(file_path)
        return {"status": "success", "detail": f"Документ {file.filename} успешно загружен и добавлен в базу RAG."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки документа: {str(e)}")

# --- Обработка диалога и генерация строгого ответа AI ---

@app.post("/api/chats/{chat_id}/prompt")
async def process_prompt(chat_id: str, payload: PromptRequest, db: Session = Depends(get_db)):
    """Принимает вопрос, ищет контекст законов и обращается к DeepSeek"""
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Сессия диалога не найдена")
    
    # 1. Сохраняем входящий вопрос пользователя в историю
    user_msg = Message(chat_id=chat_id, sender="user", text=payload.message)
    db.add(user_msg)
    
    # 2. Вытаскиваем статьи законов через семантический векторный поиск ChromaDB
    context = rag_service.search_context(payload.message)
    
    try:
        # 3. Генерируем структурированный ответ на базе контекста через DeepSeek API
        ai_json_raw = await ai_service.generate_response(payload.message, context)
        
        # 4. Если чат новый, переименовываем его заголовок по сути вопроса
        if chat.title == "Новый диалог":
            chat.title = payload.message[:35] + "..."
            db.add(chat)
        
        # 5. Сохраняем структурированные данные AI в историю базы SQLite
        ai_msg = Message(chat_id=chat_id, sender="ai", structured_data=ai_json_raw)
        db.add(ai_msg)
        db.commit()
        
        # Возвращаем клиенту валидный JSON объект для парсинга на фронтенде
        return json.loads(ai_json_raw)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Критическая ошибка нейросети: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("solution:app", host="0.0.0.0", port=8000, reload=True)