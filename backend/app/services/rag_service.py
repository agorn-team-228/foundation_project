import os
import uuid
from pypdf import PdfReader
from docx import Document as DocxDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb

class RAGService:
    def __init__(self):
        os.makedirs("./data/chroma_db", exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(name="laws_collection")
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)

    def extract_text(self, file_path: str) -> str:
        ext = os.path.splitext(file_path).lower()
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
        raw_text = self.extract_text(file_path)
        if not raw_text.strip():
            return
        chunks = self.text_splitter.split_text(raw_text)
        if chunks:
            ids = [str(uuid.uuid4()) for _ in chunks]
            metadatas = [{"source": os.path.basename(file_path)} for _ in chunks]
            self.collection.add(documents=chunks, ids=ids, metadatas=metadatas)

    def search_context(self, query: str, n_results: int = 3) -> str:
        results = self.collection.query(query_texts=[query], n_results=n_results)
        documents = results.get("documents", [])
        if documents and len(documents) > 0 and len(documents[0]) > 0:
            return "\n\n---\n\n".join(documents[0])
        return "Вгруженная законодательная база не содержит информации по данному запросу."
