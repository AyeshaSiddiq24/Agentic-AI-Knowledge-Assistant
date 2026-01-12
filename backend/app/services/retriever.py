from langchain_community.vectorstores import FAISS



def get_retriever(
    vectorstore: FAISS,
    top_k: int = 4
):
    """
    Create a retriever from the vector store.
    """

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": top_k}
    )
    return retriever
