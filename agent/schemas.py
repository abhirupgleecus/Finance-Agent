from pydantic import BaseModel
from typing import Optional, List


class FinancialProfile(BaseModel):
    income: Optional[float] = None
    income_period: Optional[str] = None  
    sip: Optional[float] = None
    savings: Optional[float] = None
    age: Optional[int] = None


class FinancialSummary(BaseModel):
    summary: str
    suggestions: List[str]