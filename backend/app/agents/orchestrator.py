# app/agents/orchestrator.py

import os
import re
from datetime import datetime
import wikipedia
from huggingface_hub import InferenceClient


class AgenticKnowledgeAssistant:
    def __init__(self, vectorstore=None):
        self.vectorstore = vectorstore

        # 🔹 Hugging Face native client (NO LangChain)
        self.client = InferenceClient(
            model=os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.2"),
            token=os.getenv("HF_API_TOKEN"),
        )

    # -----------------------------
    # TOOL ROUTING (Date / Math)
    # -----------------------------
    def is_date_question(self, question: str) -> bool:
        q = question.lower().strip()
        return any(phrase in q for phrase in [
            "today's date",
            "todays date",
            "current date",
            "what date is it",
            "what is the date",
            "today date",
            "current day",
            "what day is it",
        ])

    def is_math_question(self, question: str) -> bool:
        q = question.lower().strip()
        # Simple detection: contains digits + math operators/keywords
        has_digit = any(ch.isdigit() for ch in q)
        has_op = any(op in q for op in ["+", "-", "*", "/", "%", "^", "plus", "minus", "times", "divide", "multiplied"])
        return has_digit and has_op

    def safe_calculate(self, expr: str):
        """
        Very safe calculator:
        Allows only digits, spaces, and basic operators + - * / ( ) . %
        """
        allowed = re.compile(r"^[0-9\.\+\-\*\/\(\)\s%]+$")
        expr = expr.replace("^", "**")  # optional power support if user uses ^
        if not allowed.match(expr):
            return None
        try:
            # eval with empty builtins (prevents dangerous access)
            return eval(expr, {"__builtins__": {}}, {})
        except Exception:
            return None

    # -----------------------------
    # Wikipedia helpers
    # -----------------------------
    def normalize_query_for_wikipedia(self, query: str) -> str:
        q = query.lower().strip()
        q = re.sub(r"[?!.]", "", q)

        # Special: current president
        if "president of usa" in q or "president of the united states" in q:
            return "Current President of the United States"

        # WHO questions
        if q.startswith("who is"):
            return q.replace("who is", "").strip()

        if q.startswith("who was"):
            return q.replace("who was", "").strip()

        if q.startswith("who founded"):
            return q.replace("who founded", "").strip() + " founders"

        # WHAT questions
        if q.startswith("what is"):
            return q.replace("what is", "").strip()

        if q.startswith("what are"):
            return q.replace("what are", "").strip()

        # WHEN / WHERE
        if q.startswith("when was"):
            return q.replace("when was", "").strip()

        if q.startswith("where is"):
            return q.replace("where is", "").strip()

        return query.strip()

    def try_wikipedia(self, query: str):
        try:
            wikipedia.set_lang("en")
            normalized = self.normalize_query_for_wikipedia(query)

            # 1 sentence only = simple UX
            return wikipedia.summary(
                normalized,
                sentences=1,
                auto_suggest=True,
                redirect=True
            )
        except Exception:
            return None

    # -----------------------------
    # LLM helper (HF)
    # -----------------------------
    def hf_answer(self, prompt: str) -> str:
        response = self.client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=256,
            temperature=0.3,
        )
        return response.choices[0].message["content"]

    # -----------------------------
    # Main ASK method
    # -----------------------------
    def ask(self, question: str):
        q = question.strip()

        # 0️⃣ TOOL: Date
        if self.is_date_question(q):
            today = datetime.now().strftime("%B %d, %Y")
            return {
                "answer": f"Today's date is {today}.",
                "evaluation": {
                    "grounded": True,
                    "hallucination_risk": False,
                    "confidence": 1.0,
                },
                "trace": {
                    "provider": "system",
                    "tool": "datetime",
                    "answer_type": "tool_date",
                    "retrieval": False,
                },
            }

        # 0️⃣ TOOL: Calculator
        if self.is_math_question(q):
            # Extract math-like substring (simple)
            expr = re.sub(r"[^0-9\.\+\-\*\/\(\)\s%^%]", "", q)
            result = self.safe_calculate(expr)
            if result is not None:
                return {
                    "answer": str(result),
                    "evaluation": {
                        "grounded": True,
                        "hallucination_risk": False,
                        "confidence": 1.0,
                    },
                    "trace": {
                        "provider": "system",
                        "tool": "calculator",
                        "answer_type": "tool_math",
                        "retrieval": False,
                    },
                }

        # 1️⃣ RAG (document-based)
        context = ""
        if self.vectorstore:
            docs = self.vectorstore.similarity_search(q, k=4)
            if docs:
                context = "\n\n".join(d.page_content for d in docs)

        if context:
            prompt = f"""
You are a helpful assistant.
Answer ONLY using the context below.
If the answer is not in the context, reply exactly: Not found in document.

Context:
{context}

Question:
{q}

Answer (1-3 sentences max):
"""
            answer = self.hf_answer(prompt).strip().replace("\n", " ")
            answer_type = "document"

            return {
                "answer": answer,
                "evaluation": {
                    "grounded": True,
                    "hallucination_risk": False,
                    "confidence": 0.9,
                },
                "trace": {
                    "provider": "huggingface",
                    "model": "mistral-7b-instruct",
                    "answer_type": answer_type,
                    "retrieval": True,
                },
            }

        # 2️⃣ Wikipedia fallback (facts)
        wiki = self.try_wikipedia(q)
        if wiki:
            wiki = wiki.strip().replace("\n", " ")
            return {
                "answer": wiki,
                "evaluation": {
                    "grounded": False,              # Not grounded in user docs
                    "hallucination_risk": True,      # Still not your docs (but factual)
                    "confidence": 0.8,
                },
                "trace": {
                    "provider": "wikipedia",
                    "model": None,
                    "answer_type": "wikipedia",
                    "retrieval": False,
                },
            }

        # 3️⃣ General LLM fallback
        prompt = f"Answer clearly and concisely in 1-2 sentences:\n{q}"
        answer = self.hf_answer(prompt).strip().replace("\n", " ")

        return {
            "answer": answer,
            "evaluation": {
                "grounded": False,
                "hallucination_risk": True,
                "confidence": 0.6,
            },
            "trace": {
                "provider": "huggingface",
                "model": "mistral-7b-instruct",
                "answer_type": "general",
                "retrieval": False,
            },
        }
