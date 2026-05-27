"""
LangGraph support agent — using Groq with ReAct pattern (fully compatible).
"""
from typing import TypedDict, List, Any
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain.tools import Tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.core.config import settings
from app.db.database import SessionLocal
from app.tools.implementations import lookup_order, create_support_ticket, search_faq

SYSTEM_PROMPT = """You are a professional AI customer support agent.

You have access to these tools:
- OrderLookup: look up order status by order ID number
- FAQSearch: search FAQ for questions about refunds, shipping, returns
- CreateTicket: create a support ticket for unresolved issues

IMPORTANT: When you need to use a tool, you MUST follow this EXACT format:

Thought: I need to use a tool to help with this.
Action: ToolName
Action Input: the input to the tool
Observation: [tool result will appear here]
Thought: I now have the answer.
Final Answer: [your response to the user]

Rules:
- Always use OrderLookup when asked about an order.
- Always use FAQSearch for questions about policies, shipping, refunds.
- Always use CreateTicket for complaints or unresolved issues.
- Never make up order data — only use what tools return.
- Be concise, empathetic, and professional.
- Always end with "Final Answer:" followed by your response.
"""

class AgentState(TypedDict):
    input: str
    chat_history: List[Any]
    agent_outcome: str


def run_agent(state: AgentState) -> AgentState:
    db = SessionLocal()

    tool_map = {
        "OrderLookup": lambda x: lookup_order(x, db=db),
        "FAQSearch": search_faq,
        "CreateTicket": lambda x: create_support_ticket(x, db=db),
    }

    llm = ChatGroq(
        model=settings.MODEL_NAME,
        temperature=0,
        groq_api_key=settings.GROQ_API_KEY,
    )

    try:
        # Build conversation context
        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        for msg in state.get("chat_history", [])[-6:]:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg.get("role") == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        messages.append(HumanMessage(content=state["input"]))

        # Agentic loop — max 5 steps
        for _ in range(5):
            response = llm.invoke(messages)
            text = response.content.strip()

            # Check if done
            if "Final Answer:" in text:
                outcome = text.split("Final Answer:")[-1].strip()
                break

            # Check if tool call needed
            if "Action:" in text and "Action Input:" in text:
                try:
                    action_line = [l for l in text.split("\n") if l.startswith("Action:")][0]
                    input_line = [l for l in text.split("\n") if l.startswith("Action Input:")][0]
                    tool_name = action_line.replace("Action:", "").strip()
                    tool_input = input_line.replace("Action Input:", "").strip()

                    # Execute tool
                    if tool_name in tool_map:
                        tool_result = tool_map[tool_name](tool_input)
                    else:
                        tool_result = f"Unknown tool: {tool_name}"

                    # Add to messages and continue
                    messages.append(AIMessage(content=text))
                    messages.append(HumanMessage(content=f"Observation: {tool_result}"))
                except Exception as e:
                    outcome = text
                    break
            else:
                # Direct answer, no tool needed
                outcome = text
                break
        else:
            outcome = text

        # Clean up any leftover reasoning traces
        if "Final Answer:" in outcome:
            outcome = outcome.split("Final Answer:")[-1].strip()

    except Exception as e:
        outcome = f"I encountered an error: {str(e)}. Please try again."
    finally:
        db.close()

    return {"agent_outcome": outcome}


workflow = StateGraph(AgentState)
workflow.add_node("agent", run_agent)
workflow.set_entry_point("agent")
workflow.add_edge("agent", END)

support_graph = workflow.compile()
