from dotenv import load_dotenv
load_dotenv()   # ✅ loads .env safely

import os

from app.services.ingestion import load_documents
from app.services.chunking import chunk_documents
from app.services.vectorstore import create_vectorstore
from app.agents.orchestrator import AgenticKnowledgeAssistant


# 1️⃣ Path to a test document
TEST_FILE_PATH = "data/raw/sample.txt"

# 2️⃣ Ensure data/raw exists
os.makedirs("data/raw", exist_ok=True)

# 3️⃣ Create sample file if missing
if not os.path.exists(TEST_FILE_PATH):
    with open(TEST_FILE_PATH, "w") as f:
        f.write(
            "LangChain is a framework for building applications "
            "powered by large language models. It provides tools "
            "for retrieval, memory, agents, and evaluation."
        )

# 4️⃣ Load documents
documents = load_documents(TEST_FILE_PATH)
print(f"Loaded {len(documents)} document(s)")

# 5️⃣ Chunk documents
chunks = chunk_documents(documents)
print(f"Created {len(chunks)} chunks")

# 6️⃣ Create vector store
vectorstore = create_vectorstore(chunks)
print("Vector store created")

# 7️⃣ Initialize Agentic Assistant
assistant = AgenticKnowledgeAssistant(vectorstore)

# ------------------------------
# TEST QUESTIONS
# ------------------------------

print("\nQ1: What is LangChain?")
result1 = assistant.ask("What is LangChain?")
print("A:", result1["answer"])
print("📊 Evaluation:", result1["evaluation"])

print("\nQ2: What can it be used for?")
result2 = assistant.ask("What can it be used for?")
print("A:", result2["answer"])
print("📊 Evaluation:", result2["evaluation"])

print("\nQ3: What is 25 * 4?")
result3 = assistant.ask("25 * 4")
print("A:", result3["answer"])
print("📊 Evaluation:", result3["evaluation"])

# ------------------------------
# SOURCES (ONLY FOR RAG)
# ------------------------------

if "source_documents" in result1:
    print("\n📚 SOURCES:")
    for doc in result1["source_documents"]:
        print("-", doc.page_content[:80], "...")
