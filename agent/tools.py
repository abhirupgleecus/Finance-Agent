from langchain.tools import tool
from typing import Dict, Any


@tool
def normalize_financial_values(data: Dict[str, Any]) -> Dict[str, float]:
    """
    Normalize financial inputs into consistent monthly INR values.

    Expected input:
    {
        "income": float,
        "income_period": "monthly" | "yearly",
        "sip": float,
        "savings": float
    }
    """

    normalized: Dict[str, float] = {}

    # --- Income ---
    income = data.get("income")
    if isinstance(income, (int, float)):
        if data.get("income_period") == "yearly":
            normalized["monthly_income"] = income / 12
        else:
            normalized["monthly_income"] = float(income)

    # --- SIP / Investment ---
    sip = data.get("sip")
    if isinstance(sip, (int, float)):
        normalized["monthly_investment"] = float(sip)

    # --- Savings ---
    savings = data.get("savings")
    if isinstance(savings, (int, float)):
        normalized["total_savings"] = float(savings)

    return normalized