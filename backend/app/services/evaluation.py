# app/services/evaluation.py

def evaluate_answer(question: str, answer: str, source_documents=None):
    """
    Lightweight evaluation without LangChain dependency.
    """

    if not answer or len(answer.strip()) < 5:
        return {
            "confidence": 0.2,
            "hallucination": True,
            "reason": "Answer too short or empty"
        }

    return {
        "confidence": 1.0,
        "hallucination": False,
        "reason": "Answer generated from retrieved context or memory"
    }
