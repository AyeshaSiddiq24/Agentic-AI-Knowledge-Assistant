def build_trace(
    question: str,
    decision: str,
    answer: str,
    evaluation: dict
) -> dict:
    """
    Build a reasoning trace for transparency and debugging.
    """

    return {
        "question": question,
        "decision": decision,
        "confidence": evaluation.get("confidence"),
        "hallucination": evaluation.get("hallucination"),
        "reason": evaluation.get("reason"),
        "answer_preview": answer[:100]
    }
