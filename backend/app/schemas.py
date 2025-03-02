# backend/app/schemas.py
from pydantic import BaseModel
from typing import List

class StatementRow(BaseModel):
    date: str
    merchant_name: str
    merchant_category: str
    transaction_amount: float
    currency: str
    transaction_type: str
    remaining_credit_limit: float
    fraud_detected: bool
    explanation: str
    probability: float

class AnalyzeResponse(BaseModel):
    status: str
    rows: List[StatementRow]
