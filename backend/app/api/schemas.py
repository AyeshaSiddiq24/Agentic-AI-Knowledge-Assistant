from pydantic import BaseModel
from typing import Any, Dict

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    evaluation: Dict[str, Any]
    trace: Dict[str, Any]
