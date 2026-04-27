from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


def create_questioner(llm: ChatGoogleGenerativeAI):
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
            You generate ONE follow-up question to collect financial information.

            Rules:
            - Ask about ONLY ONE field
            - Be concise and conversational
            - Do NOT ask about multiple fields

            Field will be provided as input.
            """),
        ("human", "Field: {field}")
    ])

    return prompt | llm