# FinAssist | Wealth Intelligent Agent

FinAssist is a state-of-the-art AI-powered financial assessment tool designed to help users optimize their wealth. By leveraging advanced LLMs and a structured state machine, it transforms conversational input into actionable financial insights.

## 🚀 Overview

FinAssist acts as a virtual financial consultant. It engages in a natural conversation with the user to gather key financial data—such as income, savings, and investments—and provides a comprehensive summary along with personalized suggestions to improve their financial health.

## 🧠 Backend Architecture & Logic

The backend is built with **Python**, **LangChain**, and **Google Gemini 1.5 Flash**. It follows a modular, chain-based architecture to ensure reliability and structured data processing.

### 1. Structured Data Extraction (`agent/extractor.py`)
Unlike traditional chatbots that just "chat," FinAssist uses **Structured Output** binding. It utilizes a Pydantic schema (`FinancialProfile`) to force the LLM to return valid JSON. This allows the system to accurately parse values like "10L", "5k", or "1.2 lakh" into raw integers.

### 2. Intelligent Questioning (`agent/questioner.py`)
The system maintains a session state of the user's profile. After every input:
- It checks for missing fields (e.g., if age or savings are unknown).
- If gaps exist, the `Questioner` component dynamically generates a natural language question focused specifically on the next missing data point.
- It includes a safeguard (`MAX_QUESTIONS = 5`) to prevent infinite loops and ensure a smooth user experience.

### 3. Normalization Engine (`agent/tools.py`)
To ensure the analysis is accurate, the backend includes a normalization layer. It standardizes disparate inputs (e.g., converting yearly income to monthly, handling different currency formats) before passing them to the final analysis stage.

### 4. Financial Summarization (`agent/summarizer.py`)
Once the profile is sufficiently populated, the `Summarizer` chain analyzes the normalized metrics. It doesn't just repeat the numbers; it uses the LLM to:
- Evaluate the savings-to-income ratio.
- Assess investment consistency (SIP).
- Provide 3-5 high-impact, actionable suggestions tailored to the user's age and financial status.

### 5. State Management (`agent/state.py`)
The application uses a robust merging logic to update the user's profile incrementally. This allows users to provide information out of order or update previous values naturally during the conversation.

---

## 🛠️ Project Structure

```text
finance-agent/
├── agent/                  # Core AI Logic
│   ├── extractor.py        # Parses text into structured JSON
│   ├── questioner.py       # Generates follow-up questions
│   ├── summarizer.py       # Generates final financial report
│   ├── schemas.py          # Pydantic data models
│   ├── state.py            # Profile merging & gap analysis
│   ├── tools.py            # Normalization & data cleaning
│   └── prompts.py          # LLM system prompts
├── .streamlit/             # Streamlit configuration
├── app.py                  # Main Streamlit UI & Orchestration
├── run.py                  # CLI version of the agent
└── .env                    # Environment variables (API Keys)
```

---

## ⚙️ Setup Guide

### 1. Prerequisites
- Python 3.9+
- A Google Gemini API Key (obtain from [Google AI Studio](https://aistudio.google.com/))

### 2. Installation
Clone the repository and install the required dependencies:

```bash
git clone <your-repo-url>
cd finance-agent
pip install streamlit langchain-google-genai python-dotenv pydantic
```

### 3. Environment Configuration
Create a `.env` file in the root directory and add your API key:

```env
GOOGLE_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

### 4. Running the Application

**To launch the Web UI (Recommended):**
```bash
streamlit run app.py
```

**To launch the CLI version:**
```bash
python run.py
```

---

## 🎨 UI Aesthetics
The web interface features a premium, modern design with:
- **Glassmorphism** panels and subtle radial gradients.
- **Real-time profile tracking** in the sidebar.
- **Streaming text responses** for a natural conversational feel.
- **Responsive layout** optimized for both desktop and mobile.
