from dotenv import load_dotenv
import os

load_dotenv()
print("OPENAI_API_KEY loaded:", bool(os.getenv("OPENAI_API_KEY")))

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil

from app.services.ingestion import load_documents
from app.services.chunking import chunk_documents
from app.services.vectorstore import create_vectorstore
from app.agents.orchestrator import AgenticKnowledgeAssistant
from app.api.schemas import AskRequest, AskResponse



app = FastAPI(title="Agentic Knowledge Assistant")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = "data/raw"
os.makedirs(DATA_DIR, exist_ok=True)

assistant: AgenticKnowledgeAssistant | None = None


@app.post("/ingest")
async def ingest_file(file: UploadFile = File(...)):
    global assistant

    file_path = os.path.join(DATA_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    docs = load_documents(file_path)
    chunks = chunk_documents(docs)
    vectorstore = create_vectorstore(chunks)

    assistant = AgenticKnowledgeAssistant(vectorstore)

    return {"filename": file.filename, "chunks": len(chunks)}


@app.post("/ask", response_model=AskResponse)
async def ask_question(payload: AskRequest):
    global assistant

    if assistant is None:
        assistant = AgenticKnowledgeAssistant(vectorstore=None)

    try:
        result = assistant.ask(payload.question)
        return AskResponse(**result)

    except Exception as e:
        print("❌ ASK ERROR:", repr(e))
        return AskResponse(
            answer="Error occurred while processing the request.",
            evaluation={"confidence": 0, "hallucination": True},
            trace={"error": str(e)},
        )
                          # 👈 TEMPORARILY re-raise

