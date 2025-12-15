
from pydantic import BaseModel, Field
from typing import Optional, Dict, List

class Transaction(BaseModel):
    txn_id: str
    user_id: str
    amount: float = Field(ge=0)
    currency: str = "USD"
    mcc: Optional[int] = None
    ip: Optional[str] = None
    device_id: Optional[str] = None
    country: Optional[str] = None
    timestamp: Optional[str] = None  # ISO8601

class ScoreResponse(BaseModel):
    score: int
    reasons: list[str]
    flags: Dict[str, bool]
