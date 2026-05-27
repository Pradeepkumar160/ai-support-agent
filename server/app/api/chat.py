"""
Chat endpoints:
  POST /chat          — synchronous chat
  WebSocket /ws/chat  — real-time chat
"""
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel, Field

from app.agents.support_agent import support_graph
from app.core.guardrails import detect_prompt_injection
from app.memory.redis_memory import get_chat, save_chat

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(default="default")


class ChatResponse(BaseModel):
    response: str
    session_id: str


# ---------------------------------------------------------------------------
# HTTP endpoint
# ---------------------------------------------------------------------------

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if detect_prompt_injection(req.message):
        raise HTTPException(status_code=400, detail="Message flagged as potentially malicious.")

    history = get_chat(req.session_id)

    try:
        result = support_graph.invoke({
            "input": req.message,
            "chat_history": history,
            "agent_outcome": None,
        })
        response_text = result.get("agent_outcome", "I couldn't process that request.")
    except Exception as e:
        logger.error(f"Agent error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Agent encountered an error.")

    # Update memory
    history.append({"role": "user", "content": req.message})
    history.append({"role": "assistant", "content": response_text})
    save_chat(req.session_id, history[-20:])  # keep last 20 turns

    return ChatResponse(response=response_text, session_id=req.session_id)


# ---------------------------------------------------------------------------
# WebSocket endpoint
# ---------------------------------------------------------------------------

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    session_id = "ws-default"
    history = get_chat(session_id)

    try:
        while True:
            data = await websocket.receive_text()

            if detect_prompt_injection(data):
                await websocket.send_text("ERROR: Message flagged as potentially malicious.")
                continue

            try:
                result = support_graph.invoke({
                    "input": data,
                    "chat_history": history,
                    "agent_outcome": None,
                })
                response_text = result.get("agent_outcome", "I couldn't process that request.")
            except Exception as e:
                logger.error(f"WebSocket agent error: {e}", exc_info=True)
                response_text = "Sorry, I encountered an error. Please try again."

            history.append({"role": "user", "content": data})
            history.append({"role": "assistant", "content": response_text})
            save_chat(session_id, history[-20:])

            await websocket.send_text(response_text)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
