from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from agent.schemas import FinancialProfile


def create_extractor(llm: ChatGoogleGenerativeAI):
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
            You extract structured financial data from user input.

            Rules:
            - Return ONLY valid JSON
            - Do not add explanations
            - Convert values like:
            - "10 lakh" → 1000000
            - "5k" → 5000
            - If unknown, return null

            Fields:
            - income (number)
            - income_period ("monthly" or "yearly")
            - sip (number)
            - savings (number)
            - age (integer)
            """),
        ("human", "{input}")
    ])

    # Structured output binding
    extractor = prompt | llm.with_structured_output(FinancialProfile)

    return extractor