from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from agent.schemas import FinancialSummary


def create_summarizer(llm: ChatGoogleGenerativeAI):
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
            You are a financial assistant generating a user-friendly financial summary.

            Rules:
            - Use provided normalized values
            - Do NOT hallucinate numbers
            - Be concise and clear
            - Provide 3 to 5 actionable suggestions
            - Suggestions should be practical and realistic

            Output format:
            - summary: short paragraph
            - suggestions: list of actionable steps
        """),
        ("human", """
            Normalized Financial Data:
            - Monthly Income: {monthly_income}
            - Monthly Investment: {monthly_investment}
            - Total Savings: {total_savings}
            - Age: {age}
        """)
    ])

    summarizer = prompt | llm.with_structured_output(FinancialSummary)

    return summarizer