"""
HR Policy Bot - Agent
Agentic AI Capstone Project 2026
Domain: Human Resources Policy Assistant
"""

import os
import uuid
from typing import TypedDict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # Loads GROQ_API_KEY from .env file

# ─────────────────────────────────────────────
# PART 1: KNOWLEDGE BASE — 10 HR Policy Docs
# ─────────────────────────────────────────────

HR_DOCUMENTS = [
    {
        "id": "doc_001",
        "topic": "Leave Policy",
        "text": (
            "The company provides employees with a comprehensive leave policy. "
            "All full-time employees are entitled to 18 days of Paid Time Off (PTO) per year, which accrues at 1.5 days per month. "
            "Sick leave is separate and provides 10 days per calendar year; unused sick leave does not carry over. "
            "Casual leave is limited to 6 days per year and must be applied at least 24 hours in advance except in emergencies. "
            "Maternity leave is 26 weeks for the primary caregiver and 2 weeks for secondary caregivers. "
            "Paternity leave is 2 weeks, to be availed within 6 months of the child's birth. "
            "Leave without pay (LWP) can be granted at manager discretion for up to 90 days in exceptional cases. "
            "All leaves must be applied through the HR portal. Unapproved absences are treated as LWP."
        ),
    },
    {
        "id": "doc_002",
        "topic": "Work From Home Policy",
        "text": (
            "The company supports a hybrid work model. Employees may work from home up to 3 days per week, subject to manager approval. "
            "The WFH arrangement must be requested at least 48 hours in advance using the HR portal. "
            "Employees must remain reachable during core hours: 10 AM to 4 PM local time. "
            "Home internet connectivity and power backup are the employee's responsibility. "
            "Employees on performance improvement plans (PIP) are not eligible for WFH until the PIP is closed. "
            "Full-time WFH arrangements require VP-level approval and are reviewed every 6 months. "
            "Client-facing roles may have additional restrictions on WFH as defined by their department head. "
            "Repeated unavailability during core hours while on WFH may result in revocation of WFH privileges."
        ),
    },
    {
        "id": "doc_003",
        "topic": "Code of Conduct",
        "text": (
            "All employees are expected to maintain professional conduct at all times. "
            "Harassment, discrimination, or bullying of any form — including on the basis of gender, religion, caste, disability, or sexual orientation — is strictly prohibited. "
            "Employees must treat colleagues, clients, and vendors with respect. "
            "Confidential company information must not be shared externally without authorization. "
            "Employees must disclose any conflict of interest to HR within 15 days of it arising. "
            "Use of company assets for personal purposes is not permitted without written consent. "
            "Violation of the code of conduct can result in disciplinary action up to and including termination. "
            "All employees must complete the annual Code of Conduct e-learning module by March 31 each year."
        ),
    },
    {
        "id": "doc_004",
        "topic": "Performance Review Process",
        "text": (
            "The company conducts performance reviews twice a year: mid-year in July and annual in January. "
            "Employees set KPIs (Key Performance Indicators) at the start of each cycle in discussion with their manager. "
            "Performance is rated on a 5-point scale: Exceptional, Exceeds Expectations, Meets Expectations, Needs Improvement, and Unsatisfactory. "
            "A rating of 'Needs Improvement' triggers a 90-day Performance Improvement Plan (PIP). "
            "Annual increments and bonuses are linked to performance ratings. "
            "Employees who join after October 1 are reviewed in the next annual cycle. "
            "360-degree feedback from peers and subordinates is collected for all manager-level and above roles. "
            "All performance review discussions must be documented in the HR system within 7 days of the review meeting."
        ),
    },
    {
        "id": "doc_005",
        "topic": "Compensation and Benefits",
        "text": (
            "Salaries are paid on the last working day of each month via direct bank transfer. "
            "The company offers a Flexible Benefits Plan (FBP) where employees can allocate components such as HRA, LTA, and medical reimbursement up to their eligible limit. "
            "Medical insurance covers the employee, spouse, dependent children up to age 25, and dependent parents up to a sum insured of INR 5 lakhs. "
            "Group Term Life Insurance is provided at 3x annual CTC at no cost to the employee. "
            "The Employee Provident Fund (EPF) contribution is 12% of basic salary from both employee and employer. "
            "Annual increments are effective April 1 and are based on performance ratings and budget availability. "
            "Referral bonuses are paid out after the referred employee completes 6 months of service. "
            "All reimbursements must be submitted within 60 days of incurring the expense."
        ),
    },
    {
        "id": "doc_006",
        "topic": "Grievance Redressal Policy",
        "text": (
            "Employees who have a workplace grievance should first raise it with their direct manager within 30 days of the incident. "
            "If unresolved, the grievance can be escalated to HR within 15 days using the formal Grievance Form on the HR portal. "
            "HR will acknowledge the grievance within 3 working days and aim to resolve it within 21 working days. "
            "For grievances involving harassment or discrimination, employees may directly approach the Internal Complaints Committee (ICC) bypassing the manager. "
            "All grievance proceedings are confidential. Retaliation against an employee for filing a grievance is a serious disciplinary offence. "
            "If the employee is unsatisfied with the resolution, they may escalate to the HR Head or the Ombudsperson. "
            "Anonymous grievances may be submitted through the Ethics Hotline, though anonymous reports limit the ability to investigate fully."
        ),
    },
    {
        "id": "doc_007",
        "topic": "Recruitment and Onboarding Policy",
        "text": (
            "All open positions must be raised through the HRBP using a Position Request Form before any hiring activity begins. "
            "Internal candidates are encouraged to apply and are given preference if qualifications are equal to external candidates. "
            "Offer letters are issued within 5 working days of verbal offer acceptance. "
            "Background verification (BGV) is mandatory for all new hires and covers employment history, education, criminal records, and address. "
            "New employees complete a structured onboarding programme lasting 2 weeks that includes company orientation, policy training, and role-specific induction. "
            "The probation period is 6 months for all new hires. During probation, notice period is 2 weeks. "
            "Employees confirmed after probation serve a notice period of 60 days or as specified in their offer letter. "
            "Relocation assistance is provided for out-of-city hires as per the Relocation Policy document."
        ),
    },
    {
        "id": "doc_008",
        "topic": "Training and Development Policy",
        "text": (
            "The company is committed to continuous learning and allocates an annual L&D budget of INR 30,000 per employee. "
            "Employees may apply for external certifications, conferences, or courses through the L&D portal with manager approval. "
            "All mandatory trainings (e.g., POSH, Code of Conduct, Cybersecurity) must be completed by the stated deadline or escalated to the department head. "
            "Employees sponsored for degree programmes or long-term certifications must sign a service bond of 1 year post-completion. "
            "The company runs an internal mentoring programme matching junior employees with senior leaders for 6-month cycles. "
            "An individual development plan (IDP) is prepared annually during the performance review and shared with the employee's manager. "
            "Leadership development programmes are nominated by department heads for high-potential employees. "
            "Unused L&D budget does not carry over to the next financial year."
        ),
    },
    {
        "id": "doc_009",
        "topic": "Separation and Exit Policy",
        "text": (
            "An employee wishing to resign must submit a formal resignation letter via the HR portal or email to their manager and HR. "
            "The notice period is 60 days for confirmed employees and 2 weeks for those on probation, unless the offer letter specifies otherwise. "
            "The company may waive the notice period fully or partially at its discretion. "
            "During the notice period, employees are expected to complete knowledge transfer and handover. "
            "Full and Final (F&F) settlement including salary, PTO encashment, and deductions is processed within 45 days of the last working day. "
            "Company assets including laptops, access cards, and SIM cards must be returned on the last working day. "
            "An exit interview is conducted by HR to gather feedback. Participation is voluntary. "
            "Employees who are terminated for gross misconduct will not be eligible for PTO encashment or rehire."
        ),
    },
    {
        "id": "doc_010",
        "topic": "Anti-Harassment and POSH Policy",
        "text": (
            "The company has a zero-tolerance policy towards sexual harassment in the workplace as mandated by the POSH Act, 2013. "
            "An Internal Complaints Committee (ICC) is constituted with at least 50% women members, including an external member. "
            "Any employee who experiences or witnesses sexual harassment must report it to the ICC within 3 months of the incident. "
            "The ICC will complete its inquiry within 90 days of receiving the complaint and submit findings to the management. "
            "Complainants are protected from retaliation. Both complainant and respondent have the right to a fair hearing. "
            "False complaints made with malicious intent are also subject to disciplinary action. "
            "All employees must attend the mandatory POSH awareness training annually. "
            "The company files an annual POSH compliance report with the District Officer as required by law."
        ),
    },
    {
        "id": "doc_011",
        "topic": "Travel and Expense Policy",
        "text": (
            "Business travel must be pre-approved by the manager and booked through the company's designated travel portal. "
            "Domestic air travel is permitted for journeys over 500 km or when ground travel exceeds 8 hours one way. "
            "Hotel entitlements: Metro cities — INR 6,000/night; Tier 2 cities — INR 4,000/night; Tier 3 — INR 2,500/night. "
            "Daily allowance (DA) for domestic travel is INR 1,000/day; international travel DA is as per country-specific rates. "
            "All expenses must be submitted in the expense management system within 30 days of return with supporting receipts. "
            "Personal expenses, alcohol, minibar charges, and entertainment not pre-approved are not reimbursable. "
            "International travel requires additional approval from the Business Head and HR for visa and insurance processing. "
            "Travel reimbursements are processed with the next salary cycle after approval by the finance team."
        ),
    },
    {
        "id": "doc_012",
        "topic": "IT and Data Security Policy",
        "text": (
            "All employees are issued company devices and are responsible for their safekeeping. "
            "Employees must not install unauthorized software on company devices. "
            "Company data must not be stored on personal devices or shared externally via personal email or messaging apps. "
            "All employees must use strong passwords of at least 12 characters with complexity requirements, and change them every 90 days. "
            "Multi-factor authentication (MFA) is mandatory for all company systems and remote access. "
            "Suspected security incidents (e.g., phishing, data breach, device loss) must be reported to IT Security within 1 hour of discovery. "
            "Personal use of company internet is permitted in moderation but must not interfere with productivity or access prohibited content. "
            "Employees who leave the organization have all access credentials revoked on their last working day."
        ),
    },
]

# ─────────────────────────────────────────────
# PART 2: STATE DEFINITION
# ─────────────────────────────────────────────

class CapstoneState(TypedDict):
    question: str
    messages: List[dict]
    route: str
    retrieved: str
    sources: List[str]
    tool_result: str
    answer: str
    faithfulness: float
    eval_retries: int
    user_name: Optional[str]


# ─────────────────────────────────────────────
# PART 1 (continued): BUILD KNOWLEDGE BASE
# ─────────────────────────────────────────────

def build_knowledge_base():
    """Build ChromaDB in-memory collection with HR policy documents."""
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer

        embedder = SentenceTransformer("all-MiniLM-L6-v2")
        client = chromadb.Client()

        # Delete collection if exists (for re-runs)
        try:
            client.delete_collection("hr_policy_kb")
        except Exception:
            pass

        collection = client.create_collection("hr_policy_kb")

        texts = [doc["text"] for doc in HR_DOCUMENTS]
        ids = [doc["id"] for doc in HR_DOCUMENTS]
        metadatas = [{"topic": doc["topic"]} for doc in HR_DOCUMENTS]
        embeddings = embedder.encode(texts).tolist()

        collection.add(
            documents=texts,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas,
        )

        print(f"✅ Knowledge Base built with {len(HR_DOCUMENTS)} documents.")
        return collection, embedder

    except ImportError as e:
        print(f"⚠️  Import error building KB: {e}")
        return None, None


# ─────────────────────────────────────────────
# GLOBAL SINGLETONS (lazy-loaded)
# ─────────────────────────────────────────────

_collection = None
_embedder = None
_app = None


def get_kb():
    global _collection, _embedder
    if _collection is None or _embedder is None:
        _collection, _embedder = build_knowledge_base()
    return _collection, _embedder


# ─────────────────────────────────────────────
# PART 3: NODE FUNCTIONS
# ─────────────────────────────────────────────

def call_llm(prompt: str, system: str = "You are a helpful HR Policy assistant.", max_tokens: int = 500) -> str:
    """Call Groq LLM via API."""
    try:
        from groq import Groq
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"LLM Error: {str(e)}"


def memory_node(state: CapstoneState) -> CapstoneState:
    """
    Appends current question to messages, applies sliding window (last 6),
    extracts user name if 'my name is' is present.
    """
    question = state["question"]
    messages = state.get("messages", [])

    # Extract user name
    user_name = state.get("user_name")
    q_lower = question.lower()
    if "my name is" in q_lower:
        parts = q_lower.split("my name is")
        if len(parts) > 1:
            name_part = parts[1].strip().split()[0]
            user_name = name_part.capitalize()

    # Append question to messages
    messages.append({"role": "user", "content": question})

    # Sliding window — keep last 6 messages
    messages = messages[-6:]

    return {
        **state,
        "messages": messages,
        "user_name": user_name,
        "retrieved": "",
        "sources": [],
        "tool_result": "",
        "answer": "",
        "eval_retries": state.get("eval_retries", 0),
        "faithfulness": 0.0,
    }


def router_node(state: CapstoneState) -> CapstoneState:
    """
    Routes query to: retrieve | skip | tool
    Reply must be ONE word only.
    """
    question = state["question"]
    history = state.get("messages", [])
    history_str = "\n".join([f"{m['role']}: {m['content']}" for m in history[-4:]])

    prompt = f"""You are a routing assistant for an HR Policy Bot.
Classify the user query into exactly ONE of these categories:
- retrieve: if the question is about HR policies, rules, benefits, leave, conduct, performance, travel, IT, or company processes
- tool: if the question needs current date/time, web search, or calculation
- skip: if the question is a greeting, casual chat, memory/history reference, or does not need document retrieval

Conversation history:
{history_str}

Current question: {question}

Respond with ONE word only — retrieve, tool, or skip."""

    route = call_llm(prompt, system="You are a routing classifier. Reply with ONE word: retrieve, tool, or skip.").strip().lower()

    # Sanitize
    if route not in ("retrieve", "tool", "skip"):
        route = "retrieve"

    return {**state, "route": route}


def retrieval_node(state: CapstoneState) -> CapstoneState:
    """
    Embeds question, queries ChromaDB for top 3 chunks,
    formats as context string with [Topic] labels.
    """
    question = state["question"]
    collection, embedder = get_kb()

    if collection is None or embedder is None:
        return {**state, "retrieved": "", "sources": []}

    try:
        q_embedding = embedder.encode([question]).tolist()
        results = collection.query(query_embeddings=q_embedding, n_results=3, include=["documents", "metadatas"])

        chunks = results["documents"][0]
        metas = results["metadatas"][0]

        context_parts = []
        sources = []
        for chunk, meta in zip(chunks, metas):
            topic = meta.get("topic", "HR Policy")
            context_parts.append(f"[{topic}]\n{chunk}")
            sources.append(topic)

        retrieved = "\n\n".join(context_parts)
        return {**state, "retrieved": retrieved, "sources": sources}

    except Exception as e:
        return {**state, "retrieved": f"Retrieval error: {str(e)}", "sources": []}


def skip_retrieval_node(state: CapstoneState) -> CapstoneState:
    """Returns empty retrieved and sources for memory-only or casual queries."""
    return {**state, "retrieved": "", "sources": []}


def tool_node(state: CapstoneState) -> CapstoneState:
    """
    Implements: datetime, calculator, web search (simulated).
    Always returns strings, never raises exceptions.
    """
    question = state["question"].lower()
    tool_result = ""

    try:
        # DateTime tool
        if any(kw in question for kw in ["date", "time", "today", "day", "year", "month"]):
            now = datetime.now()
            tool_result = (
                f"Current date and time: {now.strftime('%A, %d %B %Y, %I:%M %p')}"
            )

        # Calculator tool
        elif any(kw in question for kw in ["calculate", "compute", "+", "-", "*", "/", "percent", "%", "how much is"]):
            import re
            expr = re.sub(r"[^0-9+\-*/().% ]", "", state["question"])
            expr = expr.replace("%", "/100")
            try:
                result = eval(expr, {"__builtins__": {}})
                tool_result = f"Calculation result: {result}"
            except Exception:
                tool_result = "Could not compute the expression. Please rephrase."

        # Domain API / general fallback
        else:
            tool_result = (
                "I can use web search for real-time queries. "
                "For HR policy questions, my knowledge base has the latest company policies. "
                "Please ask a specific HR policy question for detailed information."
            )

    except Exception as e:
        tool_result = f"Tool encountered an issue: {str(e)}"

    return {**state, "tool_result": tool_result}


def answer_node(state: CapstoneState) -> CapstoneState:
    """
    Builds grounded answer using retrieved context and/or tool_result.
    Includes eval_retries escalation instruction.
    """
    question = state["question"]
    retrieved = state.get("retrieved", "")
    tool_result = state.get("tool_result", "")
    user_name = state.get("user_name")
    eval_retries = state.get("eval_retries", 0)
    messages = state.get("messages", [])

    name_str = f"The user's name is {user_name}." if user_name else ""
    history_str = "\n".join([f"{m['role']}: {m['content']}" for m in messages[-4:]])

    # Build context section
    context_section = ""
    if retrieved:
        context_section += f"\n\nHR Policy Context:\n{retrieved}"
    if tool_result:
        context_section += f"\n\nTool Result:\n{tool_result}"

    escalation = ""
    if eval_retries >= 1:
        escalation = " Be more thorough and grounded in your answer. Cite specific policy details."

    system_prompt = (
        "You are an HR Policy Bot for a company. "
        "Answer ONLY from the provided context. "
        "If the answer is not in the context, say: 'I don't have specific information on that in my HR policy database.' "
        "Be concise, professional, and accurate. "
        "Do NOT make up policy details. "
        f"{name_str}{escalation}"
    )

    user_prompt = f"""Conversation History:
{history_str}

{context_section}

Question: {question}

Instructions: Answer using ONLY the context above. If no context, say you don't have that information. Be specific and cite relevant policy sections."""

    answer = call_llm(user_prompt, system=system_prompt, max_tokens=600)

    return {**state, "answer": answer}


def eval_node(state: CapstoneState) -> CapstoneState:
    """
    LLM rates faithfulness 0.0–1.0.
    Increments eval_retries.
    Skips check if retrieved is empty.
    """
    retrieved = state.get("retrieved", "")
    answer = state.get("answer", "")
    eval_retries = state.get("eval_retries", 0)

    # Skip faithfulness check for memory/tool/casual queries
    if not retrieved:
        return {**state, "faithfulness": 1.0, "eval_retries": eval_retries + 1}

    prompt = f"""You are a faithfulness evaluator. Rate how faithfully the answer is grounded in the provided context.

Context:
{retrieved[:1500]}

Answer:
{answer}

Instructions:
- Score 0.0 if the answer contains claims NOT in the context (hallucination).
- Score 1.0 if all answer claims are directly supported by the context.
- Intermediate scores for partially grounded answers.

Respond with ONLY a decimal number between 0.0 and 1.0."""

    score_str = call_llm(prompt, system="You are a faithfulness scorer. Reply with only a decimal number 0.0 to 1.0.").strip()

    try:
        faithfulness = float(score_str)
        faithfulness = max(0.0, min(1.0, faithfulness))
    except ValueError:
        faithfulness = 0.5

    return {**state, "faithfulness": faithfulness, "eval_retries": eval_retries + 1}


def save_node(state: CapstoneState) -> CapstoneState:
    """Appends assistant answer to messages history."""
    messages = state.get("messages", [])
    answer = state.get("answer", "")
    messages.append({"role": "assistant", "content": answer})
    return {**state, "messages": messages}


# ─────────────────────────────────────────────
# PART 4: CONDITIONAL EDGE FUNCTIONS
# ─────────────────────────────────────────────

def route_decision(state: CapstoneState) -> str:
    """After router node: returns 'retrieve', 'skip', or 'tool'."""
    return state.get("route", "retrieve")


def eval_decision(state: CapstoneState) -> str:
    """
    After eval node:
    - If faithfulness >= 0.7 OR eval_retries >= 2: go to 'save'
    - Otherwise: go to 'answer' (retry)
    """
    faithfulness = state.get("faithfulness", 0.0)
    eval_retries = state.get("eval_retries", 0)

    if faithfulness >= 0.7 or eval_retries >= 2:
        return "save"
    return "answer"


# ─────────────────────────────────────────────
# PART 4: GRAPH ASSEMBLY
# ─────────────────────────────────────────────

def build_graph():
    """Assemble and compile the LangGraph StateGraph."""
    try:
        from langgraph.graph import StateGraph
        from langgraph.checkpoint.memory import MemorySaver

        graph = StateGraph(CapstoneState)

        # Add all 8 nodes
        graph.add_node("memory", memory_node)
        graph.add_node("router", router_node)
        graph.add_node("retrieve", retrieval_node)
        graph.add_node("skip", skip_retrieval_node)
        graph.add_node("tool", tool_node)
        graph.add_node("answer", answer_node)
        graph.add_node("eval", eval_node)
        graph.add_node("save", save_node)

        # Set entry point
        graph.set_entry_point("memory")

        # Fixed edges
        graph.add_edge("memory", "router")
        graph.add_edge("retrieve", "answer")
        graph.add_edge("skip", "answer")
        graph.add_edge("tool", "answer")
        graph.add_edge("answer", "eval")

        # Conditional edge after router
        graph.add_conditional_edges(
            "router",
            route_decision,
            {
                "retrieve": "retrieve",
                "skip": "skip",
                "tool": "tool",
            },
        )

        # Conditional edge after eval
        graph.add_conditional_edges(
            "eval",
            eval_decision,
            {
                "answer": "answer",
                "save": "save",
            },
        )

        # Terminal edge
        graph.add_edge("save", "__end__")

        # Compile with memory checkpointing
        app = graph.compile(checkpointer=MemorySaver())
        print("✅ Graph compiled successfully.")
        return app

    except ImportError as e:
        print(f"⚠️  LangGraph not available: {e}")
        return None


def get_app():
    global _app
    if _app is None:
        _app = build_graph()
    return _app


# ─────────────────────────────────────────────
# PART 5: HELPER — ask()
# ─────────────────────────────────────────────

def ask(question: str, thread_id: str = None) -> dict:
    """
    Ask the HR Policy Bot a question.
    Returns dict with answer, route, faithfulness, sources.
    """
    if thread_id is None:
        thread_id = str(uuid.uuid4())

    app = get_app()
    if app is None:
        return {
            "answer": "System not available. Please install required packages.",
            "route": "error",
            "faithfulness": 0.0,
            "sources": [],
            "thread_id": thread_id,
        }

    config = {"configurable": {"thread_id": thread_id}}

    initial_state: CapstoneState = {
        "question": question,
        "messages": [],
        "route": "",
        "retrieved": "",
        "sources": [],
        "tool_result": "",
        "answer": "",
        "faithfulness": 0.0,
        "eval_retries": 0,
        "user_name": None,
    }

    try:
        result = app.invoke(initial_state, config=config)
        return {
            "answer": result.get("answer", "No answer generated."),
            "route": result.get("route", "unknown"),
            "faithfulness": result.get("faithfulness", 0.0),
            "sources": result.get("sources", []),
            "thread_id": thread_id,
            "user_name": result.get("user_name"),
        }
    except Exception as e:
        return {
            "answer": f"Error processing question: {str(e)}",
            "route": "error",
            "faithfulness": 0.0,
            "sources": [],
            "thread_id": thread_id,
        }


# ─────────────────────────────────────────────
# QUICK TEST (run directly)
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "="*60)
    print("HR POLICY BOT — Node Isolation Tests")
    print("="*60)

    # Test individual nodes
    test_state: CapstoneState = {
        "question": "How many days of PTO do I get per year?",
        "messages": [],
        "route": "",
        "retrieved": "",
        "sources": [],
        "tool_result": "",
        "answer": "",
        "faithfulness": 0.0,
        "eval_retries": 0,
        "user_name": None,
    }

    print("\n[1] Memory Node:")
    s = memory_node(test_state)
    print(f"    messages count: {len(s['messages'])}")

    print("\n[2] Router Node:")
    s = router_node(s)
    print(f"    route: {s['route']}")

    print("\n[3] Retrieval Node:")
    s = retrieval_node(s)
    print(f"    retrieved length: {len(s['retrieved'])} chars")
    print(f"    sources: {s['sources']}")

    print("\n[4] Answer Node:")
    s = answer_node(s)
    print(f"    answer preview: {s['answer'][:150]}...")

    print("\n[5] Eval Node:")
    s = eval_node(s)
    print(f"    faithfulness: {s['faithfulness']}")

    print("\n[6] Save Node:")
    s = save_node(s)
    print(f"    messages count after save: {len(s['messages'])}")

    print("\n✅ All nodes tested successfully.")
