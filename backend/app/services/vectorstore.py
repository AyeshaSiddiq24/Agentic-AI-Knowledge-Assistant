from typing import List
import os

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from app.services.embeddings import get_embeddings

INDEX_PATH = "data/index/faiss"


def create_vectorstore(chunks: List[Document]) -> FAISS:
    """
    Create and persist a FAISS vector store from document chunks.
    """
    embeddings = get_embeddings()

    # Build vectorstore
    vectorstore = FAISS.from_documents(
        chunks,
        embeddings
    )

    # Ensure directory exists
    os.makedirs(INDEX_PATH, exist_ok=True)

    # Save vectorstore
    vectorstore.save_local(
        INDEX_PATH,
        index_name="faiss_index"
    )

    return vectorstore


def load_vectorstore() -> FAISS:
    """
    Load an existing FAISS vector store from disk.
    """
    embeddings = get_embeddings()

    return FAISS.load_local(
        INDEX_PATH,
        embeddings,
        index_name="faiss_index",
        allow_dangerous_deserialization=True
    )
