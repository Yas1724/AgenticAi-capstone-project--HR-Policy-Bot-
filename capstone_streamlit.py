"""
HR Policy Bot — Streamlit UI
Agentic AI Capstone Project 2026
Run: streamlit run capstone_streamlit.py
"""

import streamlit as st
import uuid
import time
from dotenv import load_dotenv

load_dotenv()  # Loads GROQ_API_KEY from .env file

# ─────────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="HR Policy Bot",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d6a4f 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .main-header h1 { margin: 0; font-size: 2rem; }
    .main-header p  { margin: 0.3rem 0 0 0; opacity: 0.85; font-size: 0.95rem; }

    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-size: 0.85rem;
        color: #475569;
    }
    .source-badge {
        display: inline-block;
        background: #dbeafe;
        color: #1d4ed8;
        border-radius: 12px;
        padding: 2px 10px;
        font-size: 0.78rem;
        margin: 2px;
    }
    .route-badge {
        display: inline-block;
        border-radius: 12px;
        padding: 2px 10px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .route-retrieve { background: #dcfce7; color: #15803d; }
    .route-skip     { background: #fef9c3; color: #854d0e; }
    .route-tool     { background: #f3e8ff; color: #7c3aed; }
    .route-error    { background: #fee2e2; color: #b91c1c; }

    .chat-user     { text-align: right; }
    .chat-bot      { text-align: left; }
    .stChatMessage { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Cached resource — heavy initialisations
# ─────────────────────────────────────────────
@st.cache_resource
def load_system():
    """Load KB, embedder, and compiled graph ONCE. Cached across sessions."""
    from agent import get_kb, get_app
    collection, embedder = get_kb()
    app = get_app()
    return collection, embedder, app


# ─────────────────────────────────────────────
# Session State Initialisation
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0

if "avg_faithfulness" not in st.session_state:
    st.session_state.avg_faithfulness = []

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏢 HR Policy Bot")
    st.markdown("---")

    st.markdown("### 📋 Domain")
    st.markdown("**Human Resources Policy Assistant**")
    st.markdown("Ask me anything about company HR policies, rules, and procedures.")

    st.markdown("---")
    st.markdown("### 📚 Topics Covered")
    topics = [
        "🗓️ Leave Policy",
        "🏠 Work From Home",
        "⚖️ Code of Conduct",
        "📊 Performance Reviews",
        "💰 Compensation & Benefits",
        "🤝 Grievance Redressal",
        "👥 Recruitment & Onboarding",
        "📈 Training & Development",
        "🚪 Separation & Exit",
        "🛡️ Anti-Harassment / POSH",
        "✈️ Travel & Expense",
        "💻 IT & Data Security",
    ]
    for t in topics:
        st.markdown(f"- {t}")

    st.markdown("---")
    st.markdown("### 📊 Session Stats")
    col1, col2 = st.columns(2)
    col1.metric("Queries", st.session_state.total_queries)
    avg_faith = (
        sum(st.session_state.avg_faithfulness) / len(st.session_state.avg_faithfulness)
        if st.session_state.avg_faithfulness
        else 0.0
    )
    col2.metric("Avg Faithfulness", f"{avg_faith:.2f}")

    st.markdown("---")
    if st.button("🔄 New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.total_queries = 0
        st.session_state.avg_faithfulness = []
        st.rerun()

    st.markdown("---")
    st.markdown("### 💡 Sample Questions")
    sample_qs = [
        "How many PTO days do I get?",
        "What is the WFH policy?",
        "How do I raise a grievance?",
        "What is the notice period?",
        "Tell me about the POSH policy.",
        "What is the travel allowance for metro cities?",
        "How does the performance review work?",
    ]
    for q in sample_qs:
        if st.button(q, key=f"sample_{q}", use_container_width=True):
            st.session_state["prefill_question"] = q
            st.rerun()

# ─────────────────────────────────────────────
# Main Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🏢 HR Policy Bot</h1>
    <p>Your intelligent assistant for all company HR policies and procedures. Ask me anything!</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Load system (with spinner on first load)
# ─────────────────────────────────────────────
with st.spinner("⚙️ Loading HR Policy Knowledge Base..."):
    try:
        collection, embedder, app = load_system()
        if collection is None:
            st.error("⚠️ Knowledge base failed to load. Check dependencies.")
        else:
            st.success(f"✅ Knowledge Base loaded with 12 HR policy documents.", icon="✅")
    except Exception as e:
        st.error(f"System load error: {e}")
        collection, embedder, app = None, None, None

# ─────────────────────────────────────────────
# Render Chat History
# ─────────────────────────────────────────────
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    with st.chat_message(role):
        st.markdown(content)
        if role == "assistant" and "meta" in msg:
            meta = msg["meta"]
            col1, col2, col3 = st.columns([2, 2, 4])
            route = meta.get("route", "")
            route_class = f"route-{route}" if route in ("retrieve", "skip", "tool") else "route-error"
            col1.markdown(
                f'<span class="route-badge {route_class}">Route: {route.upper()}</span>',
                unsafe_allow_html=True,
            )
            faith = meta.get("faithfulness", 0.0)
            faith_emoji = "🟢" if faith >= 0.7 else "🟡" if faith >= 0.4 else "🔴"
            col2.markdown(f"{faith_emoji} Faithfulness: **{faith:.2f}**")
            sources = meta.get("sources", [])
            if sources:
                badges = "".join([f'<span class="source-badge">{s}</span>' for s in sources])
                col3.markdown(f"📚 {badges}", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Chat Input
# ─────────────────────────────────────────────
prefill = st.session_state.pop("prefill_question", None)

user_input = st.chat_input("Ask an HR policy question... (e.g., 'How many sick leaves do I get?')")

# Allow sidebar sample questions to prefill
if prefill and not user_input:
    user_input = prefill

if user_input and user_input.strip():
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate bot response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching HR policies..."):
            try:
                from agent import ask
                result = ask(user_input, thread_id=st.session_state.thread_id)

                answer = result.get("answer", "I couldn't generate an answer.")
                route = result.get("route", "unknown")
                faithfulness = result.get("faithfulness", 0.0)
                sources = result.get("sources", [])

                st.markdown(answer)

                # Metadata display
                col1, col2, col3 = st.columns([2, 2, 4])
                route_class = f"route-{route}" if route in ("retrieve", "skip", "tool") else "route-error"
                col1.markdown(
                    f'<span class="route-badge {route_class}">Route: {route.upper()}</span>',
                    unsafe_allow_html=True,
                )
                faith_emoji = "🟢" if faithfulness >= 0.7 else "🟡" if faithfulness >= 0.4 else "🔴"
                col2.markdown(f"{faith_emoji} Faithfulness: **{faithfulness:.2f}**")
                if sources:
                    badges = "".join([f'<span class="source-badge">{s}</span>' for s in sources])
                    col3.markdown(f"📚 {badges}", unsafe_allow_html=True)

                # Update session state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "meta": {"route": route, "faithfulness": faithfulness, "sources": sources},
                })
                st.session_state.total_queries += 1
                st.session_state.avg_faithfulness.append(faithfulness)

            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#94a3b8; font-size:0.8rem;'>"
    "HR Policy Bot • Agentic AI Capstone 2026 • Powered by Groq (LLaMA 3.3) + LangGraph + ChromaDB"
    "<br>Yashraj Singh | Roll No. 2328058 | KIIT Deemed to be University"
    "</p>",
    unsafe_allow_html=True,
)
