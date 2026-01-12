# app/services/memory.py

class SimpleConversationMemory:
    def __init__(self):
        self.history = []

    def add(self, question: str, answer: str):
        self.history.append({"question": question, "answer": answer})

    def get_context(self) -> str:
        return "\n".join(
            f"Q: {h['question']}\nA: {h['answer']}"
            for h in self.history[-5:]  # last 5 turns
        )


_memory = SimpleConversationMemory()


def get_memory():
    return _memory

