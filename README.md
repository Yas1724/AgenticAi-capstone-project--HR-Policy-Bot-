# 🏢 HR Policy Bot

> An agentic AI assistant that answers employee questions about company HR policies — grounded, faithful, and hallucination-aware.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Agent Graph](#agent-graph)
- [Knowledge Base](#knowledge-base)
- [Node Reference](#node-reference)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup and Installation](#setup-and-installation)
- [Running the App](#running-the-app)
- [Environment Variables](#environment-variables)
- [Features](#features)
- [Faithfulness Evaluation](#faithfulness-evaluation)
- [Sample Questions](#sample-questions)

---

## Overview

HR Policy Bot is a capstone agentic AI project built for 2026. It uses a **LangGraph state machine** to intelligently route employee queries through a structured pipeline: memory management → query routing → retrieval or tool use → answer generation → faithfulness evaluation → response saving.

The bot is grounded entirely in a curated internal knowledge base of 12 HR policy documents and uses **Groq's LLaMA 3.3 70B** as the LLM backend. It features a polished **Streamlit** UI with real-time metadata display (route taken, faithfulness score, source documents).

---

## Architecture

```
User Question
     │
     ▼
┌──────────┐     ┌──────────┐     ┌────────────────────────────┐
│  Memory  │────▶│  Router  │────▶│  retrieve / skip / tool    │
│   Node   │     │   Node   │     └────────────────────────────┘
└──────────┘     └──────────┘                  │
                                               ▼
                                        ┌────────────┐
                                        │   Answer   │◀──(retry if low faithfulness)
                                        │    Node    │
                                        └────────────┘
                                               │
                                               ▼
                                        ┌────────────┐
                                        │    Eval    │──▶ faithfulness ≥ 0.7 or retries ≥ 2
                                        │    Node    │
                                        └────────────┘
                                               │
                                               ▼
                                        ┌────────────┐
                                        │    Save    │──▶ END
                                        │    Node    │
                                        └────────────┘
```

---

## Agent Graph

The graph is assembled using **LangGraph's StateGraph** and compiled with `MemorySaver` for in-memory checkpointing across a conversation thread.

### Nodes

| Node | Type | Description |
|------|------|-------------|
| `memory` | Entry | Appends user question to conversation history; applies a sliding window of last 6 messages; extracts user name if stated |
| `router` | Conditional | Classifies query as `retrieve`, `tool`, or `skip` using LLM |
| `retrieve` | Retrieval | Embeds query with `all-MiniLM-L6-v2`; fetches top 3 chunks from ChromaDB |
| `skip` | Pass-through | Used for greetings, casual chat, memory-only queries |
| `tool` | Tool Use | Handles datetime queries, arithmetic calculations, and fallback web search info |
| `answer` | Generation | Builds a grounded answer from retrieved context and/or tool results using Groq LLM |
| `eval` | Evaluation | LLM-based faithfulness scorer (0.0–1.0); triggers retry if score < 0.7 |
| `save` | Persistence | Appends final assistant answer to conversation messages |

### Conditional Edges

**After `router`:**
- `retrieve` → run semantic search on HR knowledge base
- `tool` → run datetime / calculator tool
- `skip` → bypass retrieval, go directly to answer

**After `eval`:**
- `answer` → retry if `faithfulness < 0.7` AND `eval_retries < 2`
- `save` → finalize if `faithfulness ≥ 0.7` OR `eval_retries ≥ 2`

---

## Knowledge Base

The knowledge base contains **12 HR policy documents** embedded using `sentence-transformers/all-MiniLM-L6-v2` and stored in an in-memory ChromaDB collection.

| Doc ID | Topic |
|--------|-------|
| doc_001 | Leave Policy |
| doc_002 | Work From Home Policy |
| doc_003 | Code of Conduct |
| doc_004 | Performance Review Process |
| doc_005 | Compensation and Benefits |
| doc_006 | Grievance Redressal Policy |
| doc_007 | Recruitment and Onboarding Policy |
| doc_008 | Training and Development Policy |
| doc_009 | Separation and Exit Policy |
| doc_010 | Anti-Harassment and POSH Policy |
| doc_011 | Travel and Expense Policy |
| doc_012 | IT and Data Security Policy |

Each document contains detailed, realistic policy text covering entitlements, procedures, timelines, and conditions.

---

## Node Reference

### `memory_node`
- Maintains conversation context with a **sliding window of last 6 messages**
- Automatically extracts the user's name if they say `"my name is ..."`
- Resets per-turn fields: `retrieved`, `sources`, `tool_result`, `answer`

### `router_node`
- Sends conversation history + current question to Groq LLM
- One-word classification: `retrieve` | `tool` | `skip`
- Falls back to `retrieve` if LLM output is unexpected

### `retrieval_node`
- Encodes the question with `all-MiniLM-L6-v2`
- Queries ChromaDB for **top 3 semantically similar chunks**
- Formats context with `[Topic]` labels for the answer node

### `tool_node`
- **Datetime:** Returns current date and time for any time-related query
- **Calculator:** Evaluates safe arithmetic expressions (no builtins)
- **Fallback:** Returns a helpful message for other tool-type queries

### `answer_node`
- Builds a grounded response from `retrieved` context and/or `tool_result`
- Personalized with user name if known
- Instructed never to fabricate policy details
- On retry (`eval_retries ≥ 1`), instructed to be more thorough and cite specific sections

### `eval_node`
- Skips faithfulness check for non-retrieval queries (assigns `1.0`)
- Prompts LLM to score how grounded the answer is in the provided context
- Score range: `0.0` (hallucination) to `1.0` (fully grounded)

### `save_node`
- Appends the final answer to the `messages` list for multi-turn continuity

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | Groq — `llama-3.3-70b-versatile` |
| Agent Framework | LangGraph (`StateGraph`, `MemorySaver`) |
| Vector Store | ChromaDB (in-memory) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| UI | Streamlit |
| Environment | Python-dotenv |

---

## Project Structure

```
HR_Policy_Bot_Submission/
│
├── agent.py                  # Core agent — knowledge base, nodes, graph, ask()
├── capstone_streamlit.py     # Streamlit UI
├── day13_capstone.ipynb      # Development notebook
└── .env                      # Environment variables (Groq API key)
```

---

## Setup and Installation

### Prerequisites

- Python 3.9 or higher
- A [Groq API key](https://console.groq.com/)

### 1. Clone / Extract the project

```bash
unzip HR_Policy_Bot_Submission.zip
cd HR_Policy_Bot_Submission
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install groq langgraph chromadb sentence-transformers streamlit python-dotenv
```

### 4. Configure environment variables

Create (or edit) the `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

---

## Running the App

### Streamlit UI (recommended)

```bash
streamlit run capstone_streamlit.py
```

The app will open at `http://localhost:8501`.

### Direct Python test

To test individual agent nodes from the terminal:

```bash
python agent.py
```

This runs the built-in node isolation tests against a sample question.

### Programmatic usage

```python
from agent import ask

result = ask("How many days of PTO do I get per year?")
print(result["answer"])
print(f"Route: {result['route']}")
print(f"Faithfulness: {result['faithfulness']}")
print(f"Sources: {result['sources']}")
```

**Return shape:**

```python
{
    "answer": str,         # Final response text
    "route": str,          # "retrieve" | "tool" | "skip" | "error"
    "faithfulness": float, # 0.0 – 1.0
    "sources": list[str],  # Policy topic names cited
    "thread_id": str,      # Conversation thread ID
    "user_name": str | None
}
```

Multi-turn conversations share a `thread_id`:

```python
tid = "my-session-123"
ask("What is the WFH policy?", thread_id=tid)
ask("Can I do it 5 days a week?", thread_id=tid)   # maintains context
```

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | API key from [console.groq.com](https://console.groq.com/) | ✅ Yes |

---

## Features

- **Agentic routing** — queries are intelligently classified before any retrieval
- **Semantic search** — top-3 relevant policy chunks fetched per query
- **Multi-turn memory** — sliding window of 6 messages maintains conversation context
- **User name persistence** — bot remembers your name within a session
- **Tool use** — handles date/time queries and arithmetic calculations
- **Faithfulness evaluation** — auto-retries if answer is not well-grounded (up to 2 retries)
- **Streamlit UI** — chat interface with route badges, faithfulness scores, and source tags
- **Session stats** — live query count and average faithfulness score in sidebar
- **Sample question buttons** — quick-start queries in the sidebar
- **New Conversation reset** — clears session state and starts a fresh thread

---

## Faithfulness Evaluation

After every answer generation, the `eval_node` scores the response on a `0.0–1.0` scale:

| Score | Meaning | UI Indicator |
|-------|---------|--------------|
| ≥ 0.7 | Fully or mostly grounded | 🟢 |
| 0.4 – 0.69 | Partially grounded | 🟡 |
| < 0.4 | Likely hallucinated | 🔴 |

If the score is below `0.7` and the answer hasn't been retried twice yet, the graph loops back to `answer_node` with an escalation instruction to be more thorough. This prevents low-quality responses from being surfaced.

---

## Sample Questions

| Question | Expected Route |
|----------|---------------|
| How many PTO days do I get per year? | `retrieve` |
| What is the WFH policy? | `retrieve` |
| How do I raise a grievance? | `retrieve` |
| What is the notice period after confirmation? | `retrieve` |
| Tell me about the POSH policy. | `retrieve` |
| What is the hotel allowance for metro cities? | `retrieve` |
| How does the annual performance review work? | `retrieve` |
| What is today's date? | `tool` |
| Calculate 12% of 50000. | `tool` |
| Hi, my name is Arjun. | `skip` |
| What did you just tell me? | `skip` |

---

## Notes

- The ChromaDB collection is **in-memory** and rebuilt on every app start. There is no persistent vector store on disk.
- The LLM is instructed never to answer from outside the knowledge base. If a question has no matching policy, it will respond: *"I don't have specific information on that in my HR policy database."*
- The `.env` file included in the submission contains a placeholder key. Replace it with your actual Groq API key before running.

---

*HR Policy Bot — Agentic AI Capstone Project 2026 | Powered by Groq (LLaMA 3.3) + LangGraph + ChromaDB*

*Yashraj Singh | Roll No. 2328058 | KIIT Deemed to be University*
