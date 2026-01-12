from app.services.chains import build_rag_chain
from app.services.evaluation import evaluate_answer
from app.core.llm import get_llm

class AgenticKnowledgeAssistant:
    def __init__(self, vectorstore):
        llm = get_llm()
        self.rag_chain = build_rag_chain(vectorstore, llm)

    def ask(self, question: str):
        answer = self.rag_chain.invoke(question)

        evaluation = evaluate_answer(
            question=question,
            answer=answer,
            source_documents=[]
        )

        return {
            "answer": answer,
            "evaluation": evaluation,
            "trace": {
                "status": "success"
            }
        }
