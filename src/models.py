from pydantic import BaseModel
from typing import List, Optional

class Observation(BaseModel):
    email_id: str
    sender: str
    subject: str
    body: str
    current_folder: str

class Action(BaseModel):
    category: str  # Options: "support", "billing", "spam"
    priority: str  # Options: "low", "medium", "high"
    reply_draft: str

class EnvResponse(BaseModel):
    observation: Optional[Observation]
    reward: float
    done: bool
    info: dict