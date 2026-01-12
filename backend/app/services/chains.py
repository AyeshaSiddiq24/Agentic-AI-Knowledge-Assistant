# app/services/chains.py

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate


def build_rag_chain(llm, retriever):
    """
    Create a LangChain RetrievalQA pipeline for document-based question answering.
    """

    template = """
You are a helpful assistant. Use ONLY the context below to answer.
If the answer is not in the context, say: "I don't know."

Context:
{context}

Question:
{question}

Answer:
"""

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=template,
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True,
    )

    return chain
