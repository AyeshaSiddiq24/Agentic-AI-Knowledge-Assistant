from fastapi import FastAPI
from dotenv import load_dotenv

# Load environment variables ONCE
load_dotenv()

app = FastAPI(
    title="Agentic AI Knowledge Assistant",
    version="0.1.0"
)

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Agentic AI Knowledge Assistant backend is running"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
