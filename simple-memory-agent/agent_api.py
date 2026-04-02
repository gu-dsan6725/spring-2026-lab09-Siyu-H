"""FastAPI wrapper around the memory Agent (Problem 2).

Run from this directory:
    uv run uvicorn agent_api:app --host 127.0.0.1 --port 9090
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agent import Agent

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Memory Agent API",
    description="Multi-tenant conversational agent with semantic memory",
    version="1.0.0",
)

# One Agent per (user_id, run_id) — required when different users reuse the same run_id string
_session_cache: Dict[str, Agent] = {}


def _session_key(user_id: str, run_id: str) -> str:
    return f"{user_id}:{run_id}"


def _get_or_create_agent(user_id: str, run_id: str) -> Agent:
    key = _session_key(user_id, run_id)
    if key in _session_cache:
        return _session_cache[key]
    agent = Agent(user_id=user_id, run_id=run_id)
    _session_cache[key] = agent
    logger.info("Created new Agent for user_id=%s run_id=%s", user_id, run_id)
    return agent


class InvocationRequest(BaseModel):
    user_id: str = Field(..., description="User identifier for memory isolation")
    query: str = Field(..., description="User message")
    run_id: Optional[str] = Field(
        default=None,
        description="Session id; auto-generated if omitted",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata (accepted for API parity; not passed to Mem0 here)",
    )


class PingResponse(BaseModel):
    status: str
    message: str


@app.get("/ping", response_model=PingResponse)
def ping() -> PingResponse:
    return PingResponse(
        status="ok",
        message="Memory Agent API is running",
    )


@app.post("/invocation")
def invocation(body: InvocationRequest) -> Dict[str, Any]:
    if not body.query or not body.query.strip():
        raise HTTPException(status_code=400, detail="query must be non-empty")
    if not body.user_id or not body.user_id.strip():
        raise HTTPException(status_code=400, detail="user_id must be non-empty")

    run_id = body.run_id.strip() if body.run_id else str(uuid.uuid4())[:8]

    try:
        agent = _get_or_create_agent(body.user_id.strip(), run_id)
        response_text = ""
        for attempt in range(3):
            response_text = agent.chat(body.query.strip())
            if response_text and response_text.strip():
                break
            logger.warning("Empty model response (attempt %s/3), retrying", attempt + 1)
            time.sleep(1.0)
    except Exception as e:
        logger.exception("invocation failed")
        raise HTTPException(status_code=500, detail=str(e)) from e

    return {"response": response_text, "run_id": run_id}
