import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

from agent.tools import normalize_financial_values
from agent.prompts import SYSTEM_PROMPT

# Load env variables
load_dotenv()


def create_agent_executor():
    llm = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL"),
        temperature=0
    )

    tools = [normalize_financial_values]

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT
    )

    return agent