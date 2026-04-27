import os
import time

import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from agent.extractor import create_extractor
from agent.questioner import create_questioner
from agent.summarizer import create_summarizer
from agent.state import get_missing_fields, merge_profiles
from agent.schemas import FinancialProfile
from agent.tools import normalize_financial_values


# --- CONFIGURATION & STYLING ---
load_dotenv()

st.set_page_config(
    page_title="FinAssist | Wealth Intelligent Agent",
    page_icon="FI",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --ink: #0f172a;
        --muted: #64748b;
        --line: #dbe3ef;
        --panel: rgba(255, 255, 255, 0.9);
        --accent: #2563eb;
        --accent-soft: #dbeafe;
        --teal: #0f766e;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(37, 99, 235, 0.12), transparent 28rem),
            linear-gradient(135deg, #f8fafc 0%, #e8eef7 52%, #dbe4f0 100%) !important;
        color: var(--ink);
    }

    .block-container {
        max-width: 1120px;
        padding: 2.25rem 2.5rem 2rem;
    }

    section[data-testid="stSidebar"] {
        background: rgba(248, 250, 252, 0.94);
        border-right: 1px solid rgba(148, 163, 184, 0.26);
        box-shadow: 12px 0 40px rgba(15, 23, 42, 0.06);
    }

    section[data-testid="stSidebar"] > div {
        padding: 2rem 1.3rem;
    }

    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.25rem;
    }

    .brand-mark {
        display: grid;
        place-items: center;
        width: 2.25rem;
        height: 2.25rem;
        border-radius: 8px;
        background: linear-gradient(135deg, #1d4ed8, #0f766e);
        color: white;
        font-weight: 800;
        box-shadow: 0 12px 24px rgba(37, 99, 235, 0.22);
    }

    .brand-title {
        font-size: 1.45rem;
        line-height: 1;
        font-weight: 800;
        color: var(--ink);
    }

    .brand-subtitle {
        color: var(--muted);
        font-size: 0.84rem;
        margin: 0.45rem 0 1.6rem;
    }

    .sidebar-rule {
        height: 1px;
        background: linear-gradient(90deg, rgba(37, 99, 235, 0.35), rgba(148, 163, 184, 0.18));
        margin: 1rem 0 1.65rem;
    }

    .sidebar-heading {
        font-size: 1.05rem;
        font-weight: 800;
        color: var(--ink);
        margin: 0 0 0.9rem;
    }

    .metric-item {
        background: rgba(255, 255, 255, 0.9);
        padding: 0.85rem 0.95rem;
        border-radius: 8px;
        border: 1px solid rgba(203, 213, 225, 0.86);
        margin-bottom: 0.65rem;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.04);
    }

    .metric-label {
        font-size: 0.68rem;
        font-weight: 800;
        color: var(--muted);
        text-transform: uppercase;
        margin-bottom: 0.28rem;
    }

    .metric-value {
        font-size: 0.96rem;
        font-weight: 800;
        color: var(--ink);
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--panel);
        border: 1px solid rgba(203, 213, 225, 0.82);
        border-radius: 10px;
        box-shadow: 0 24px 70px rgba(15, 23, 42, 0.12);
        backdrop-filter: blur(14px);
    }

    .chat-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 1rem;
        padding: 0.35rem 0.25rem 1rem;
        border-bottom: 1px solid rgba(203, 213, 225, 0.8);
    }

    .chat-title {
        margin: 0;
        font-size: clamp(1.8rem, 3vw, 2.45rem);
        line-height: 1.08;
        font-weight: 800;
        color: var(--ink);
    }

    .chat-subtitle {
        margin: 0.55rem 0 0;
        color: var(--muted);
        font-size: 0.98rem;
    }

    .chat-status {
        flex: 0 0 auto;
        border: 1px solid rgba(37, 99, 235, 0.18);
        background: var(--accent-soft);
        color: #1e40af;
        border-radius: 999px;
        padding: 0.45rem 0.8rem;
        font-size: 0.78rem;
        font-weight: 800;
    }

    .chat-window {
        padding: 1.1rem 0.15rem 0;
    }

    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        margin-bottom: 0.9rem !important;
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        padding: 0.95rem 1.1rem !important;
        border-radius: 8px !important;
        box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stMarkdownContainer"] {
        background: #ffffff !important;
        border: 1px solid rgba(203, 213, 225, 0.75) !important;
        color: #253044 !important;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stMarkdownContainer"] {
        background: #eaf2ff !important;
        border: 1px solid rgba(37, 99, 235, 0.16) !important;
        color: #172554 !important;
    }

    [data-testid="stChatInput"] {
        border-radius: 8px !important;
        border: 1px solid rgba(148, 163, 184, 0.5) !important;
        background-color: #ffffff !important;
        box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
    }

    [data-testid="stBottom"], .stChatInputContainer {
        background: transparent !important;
        border: none !important;
    }

    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: var(--ink) !important;
        font-weight: 800 !important;
    }

    #MainMenu, footer, header { visibility: hidden !important; }
    [data-testid="stHeader"] { display: none !important; }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #2563eb, #0f766e) !important;
    }

    .stProgress > div > div {
        background-color: rgba(148, 163, 184, 0.16) !important;
    }

    section[data-testid="stSidebar"] .stButton > button {
        border-radius: 8px;
        border: 1px solid rgba(148, 163, 184, 0.45);
        background: #ffffff;
        color: var(--ink);
        font-weight: 700;
        height: 2.75rem;
    }

    @media (max-width: 760px) {
        .block-container {
            padding: 1rem;
        }

        .chat-header {
            display: block;
        }

        .chat-status {
            display: inline-block;
            margin-top: 0.9rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "profile" not in st.session_state:
    st.session_state.profile = FinancialProfile()
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "last_asked_field" not in st.session_state:
    st.session_state.last_asked_field = None
if "is_complete" not in st.session_state:
    st.session_state.is_complete = False

MAX_QUESTIONS = 5


# --- BACKEND ---
@st.cache_resource
def get_llm():
    return ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        temperature=0,
    )


llm = get_llm()
extractor = create_extractor(llm)
questioner = create_questioner(llm)
summarizer_chain = create_summarizer(llm)


# --- HELPERS ---
def stream_text(text: str):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)


def reset_chat():
    st.session_state.messages = []
    st.session_state.profile = FinancialProfile()
    st.session_state.question_count = 0
    st.session_state.last_asked_field = None
    st.session_state.is_complete = False
    st.rerun()


def _message_to_text(response) -> str:
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        return " ".join(
            [i.get("text", "") if isinstance(i, dict) else str(i) for i in content]
        ).strip()
    return str(content).strip()


# --- SIDEBAR: PROFILE ---
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-mark">FI</div>
            <div class="brand-title">FinAssist</div>
        </div>
        <div class="brand-subtitle">Wealth Intelligent Agent</div>
        <div class="sidebar-rule"></div>
        <div class="sidebar-heading">Your Profile</div>
        """,
        unsafe_allow_html=True,
    )

    p = st.session_state.profile
    fields = [
        ("Monthly Income", f"Rs {p.income:,.0f}" if p.income else "Pending"),
        ("Period", p.income_period.capitalize() if p.income_period else "Pending"),
        ("Monthly SIP", f"Rs {p.sip:,.0f}" if p.sip else "Pending"),
        ("Total Savings", f"Rs {p.savings:,.0f}" if p.savings else "Pending"),
        ("Age", str(p.age) if p.age else "Pending"),
    ]

    filled = len([v for _, v in fields if v != "Pending"])
    progress = filled / len(fields)
    st.progress(progress)

    for label, value in fields:
        is_pending = value == "Pending"
        val_color = "#94A3B8" if is_pending else "#0f766e"
        st.markdown(
            f"""
            <div class="metric-item">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color: {val_color};">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    if st.button("Clear Session", use_container_width=True):
        reset_chat()


# --- MAIN UI: CHAT CONTAINER ---
with st.container(border=True):
    st.markdown(
        """
        <div class="chat-header">
            <div>
                <h1 class="chat-title">Wealth Assessment</h1>
                <p class="chat-subtitle">Let's optimize your financial future.</p>
            </div>
            <div class="chat-status">Assessment Chat</div>
        </div>
        <div class="chat-window"></div>
        """,
        unsafe_allow_html=True,
    )

    chat_container = st.container(height=500, border=False)
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if not st.session_state.messages:
            welcome = (
                "Hello! I'm your financial assistant. Tell me a bit about your finances "
                "(e.g., 'I earn 1.2L a month, I'm 30, and have 10L in savings')"
            )
            st.session_state.messages.append({"role": "assistant", "content": welcome})
            with st.chat_message("assistant"):
                st.markdown(welcome)

    if user_input := st.chat_input("How can I help with your wealth today?"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                try:
                    # 1. Extraction
                    if st.session_state.last_asked_field:
                        try:
                            clean_val = (
                                user_input.replace(",", "")
                                .replace("Rs", "")
                                .replace("rs", "")
                                .strip()
                            )
                            extracted = FinancialProfile(
                                **{st.session_state.last_asked_field: float(clean_val)}
                            )
                        except Exception:
                            extracted = extractor.invoke({"input": user_input})
                        st.session_state.last_asked_field = None
                    else:
                        extracted = extractor.invoke({"input": user_input})

                    # 2. Merge
                    st.session_state.profile = merge_profiles(
                        st.session_state.profile, extracted
                    )

                    # 3. Flow Logic
                    missing = get_missing_fields(st.session_state.profile)

                    if (
                        missing
                        and st.session_state.question_count < MAX_QUESTIONS
                        and not st.session_state.is_complete
                    ):
                        field = missing[0]
                        st.session_state.last_asked_field = field
                        resp = questioner.invoke({"field": field})
                        txt = _message_to_text(resp)
                        full_resp = st.write_stream(stream_text(txt))
                        st.session_state.messages.append(
                            {"role": "assistant", "content": full_resp}
                        )
                        st.session_state.question_count += 1
                    else:
                        st.session_state.is_complete = True
                        prof = st.session_state.profile
                        norm = normalize_financial_values.invoke(
                            {
                                "data": {
                                    "income": prof.income,
                                    "income_period": prof.income_period,
                                    "sip": prof.sip,
                                    "savings": prof.savings,
                                }
                            }
                        )
                        res = summarizer_chain.invoke(
                            {
                                "monthly_income": norm.get("monthly_income"),
                                "monthly_investment": norm.get("monthly_investment"),
                                "total_savings": norm.get("total_savings"),
                                "age": prof.age,
                            }
                        )
                        st.markdown("### Financial Summary")
                        sum_txt = st.write_stream(stream_text(res.summary))
                        st.markdown("### Suggestions")
                        sug_txt = ""
                        for i, suggestion in enumerate(res.suggestions, 1):
                            sug_txt += f"{i}. {suggestion}\n"
                        st.markdown(sug_txt)
                        combined = (
                            f"### Financial Summary\n{sum_txt}\n\n"
                            f"### Suggestions\n{sug_txt}"
                        )
                        st.session_state.messages.append(
                            {"role": "assistant", "content": combined}
                        )

                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
