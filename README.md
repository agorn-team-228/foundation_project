# Legal AI Assistant (Hybrid RAG)

Интеллектуальный ассистент для поиска и анализа юридических документов.
Использует гибридный поиск (BM25 + FAISS) и эмбеддинги aai/bge-m3.

##  Структура проекта
- `backend/` — FastAPI сервер (Python 3.11)
- `frontend/` — React + Vite интерфейс (Node.js 20)

##  Быстрый старт (Docker)

1. Убедитесь, что в папке `backend/` присутствует файл `.env` с ключами API (LLM_BASE_URL, LLM_API_KEY и т.д.).
2. В корне проекта выполните:
   `ash
   docker-compose up --build"
