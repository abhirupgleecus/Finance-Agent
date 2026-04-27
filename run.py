import os
from dotenv import load_dotenv

from agent.agent import create_agent_executor
from agent.extractor import create_extractor
from agent.questioner import create_questioner
from agent.summarizer import create_summarizer
from agent.state import merge_profiles, get_missing_fields
from agent.schemas import FinancialProfile
from agent.tools import normalize_financial_values
from langchain_google_genai import ChatGoogleGenerativeAI

# Load env variables
load_dotenv()

# LLM (reuse same model)
agent = create_agent_executor()
llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL"),
    temperature=0

) 

extractor = create_extractor(llm)
questioner = create_questioner(llm)


def _message_to_text(response) -> str:
    """
    Convert LLM responses into plain text.
    Handles providers that return content as rich blocks like:
    [{"type": "text", "text": "..."}]
    """
    content = getattr(response, "content", response)

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item.strip())
                continue

            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str) and text.strip():
                    parts.append(text.strip())
                continue

            text = getattr(item, "text", None)
            if isinstance(text, str) and text.strip():
                parts.append(text.strip())

        return " ".join(part for part in parts if part).strip()

    if isinstance(content, dict):
        text = content.get("text")
        if isinstance(text, str):
            return text.strip()

    return str(content).strip()

print("💬 Financial Agent Ready (type 'exit' to quit)\n")

# 🔥 STATE
profile = FinancialProfile()

# 🔥 QUESTION COUNT (for later constraint)
question_count = 0
MAX_QUESTIONS = 5

last_asked_field = None

while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        break

    try:
        # 1. Extract structured data
        if last_asked_field:
            # User is answering a specific question → force mapping
            extracted = FinancialProfile(**{last_asked_field: float(user_input)})
            last_asked_field = None
        else:
            extracted = extractor.invoke({"input": user_input})

        # 2. Merge into state
        profile = merge_profiles(profile, extracted)

        print(f"[DEBUG] Current State: {profile}")

        # 3. Check missing fields
        missing_fields = get_missing_fields(profile)

        # 4. If missing → ask question
        if missing_fields and question_count < MAX_QUESTIONS:
            field_to_ask = missing_fields[0]
            last_asked_field = field_to_ask

            question_response = questioner.invoke({"field": field_to_ask})
            question = _message_to_text(question_response)

            if not question:
                question = {
                    "income": "What is your income amount?",
                    "income_period": "Is your income monthly or yearly?",
                    "sip": "What is the monthly SIP amount you are currently investing?",
                    "savings": "What are your current total savings?",
                    "age": "What is your age?",
                }.get(field_to_ask, f"Please share your {field_to_ask}.")

            question_count += 1

            print("\nAgent:", question, "\n")
            continue

        # 5. Enough data → normalize
        normalized = normalize_financial_values.invoke({
            "data": {
                "income": profile.income,
                "income_period": profile.income_period,
                "sip": profile.sip,
                "savings": profile.savings
            }
        })

        print(f"[DEBUG] Normalized: {normalized}")

        summarizer = create_summarizer(llm)

        # 6. Generate summary using LLM
        summary_result = summarizer.invoke({
            "monthly_income": normalized.get("monthly_income"),
            "monthly_investment": normalized.get("monthly_investment"),
            "total_savings": normalized.get("total_savings"),
            "age": profile.age
        })

        print("\nAgent:")
        print(summary_result.summary)
        print("\nSuggestions:")
        for i, s in enumerate(summary_result.suggestions, 1):
            print(f"{i}. {s}")
        print()

        break  # stop after summary

    except Exception as e:
        print("\nError:", str(e), "\n")
