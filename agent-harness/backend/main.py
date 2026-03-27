"""
Activepieces Flow-Creation Agent Backend
=========================================
FastAPI service that exposes a streaming chat endpoint backed by Claude Opus 4.6.
The agent can create Activepieces flows by calling bash and read_file tools.

Endpoints:
  POST /chat          — send a message, get SSE stream of events
  GET  /health        — health check
  GET  /history/{id}  — retrieve conversation history (in-memory, resets on restart)
"""

import json
import os
import uuid
from pathlib import Path
from typing import AsyncIterator

import anthropic
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from system_prompt import build_system_prompt
from tools import TOOL_DEFINITIONS, dispatch_tool

# Load .env file if present (for local dev without exporting env vars)
_env_file = Path(__file__).parent / ".env"
if _env_file.exists():
    for line in _env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(title="Activepieces Flow Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_FLOW_KEY"))

# In-memory conversation store: session_id → list[message]
_conversations: dict[str, list[dict]] = {}

# Build system prompt once at startup (static for the lifetime of the process)
_SYSTEM_PROMPT = build_system_prompt()


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None  # omit to start a new conversation


class ChatResponse(BaseModel):
    session_id: str
    # (actual content arrives via SSE)


# ---------------------------------------------------------------------------
# SSE helpers
# ---------------------------------------------------------------------------


def _sse(event: str, data: dict | str) -> str:
    payload = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"


# ---------------------------------------------------------------------------
# Agentic loop with streaming
# ---------------------------------------------------------------------------


async def _agent_stream(session_id: str, messages: list[dict]) -> AsyncIterator[str]:
    """
    Runs the Claude agentic loop with tool use, yielding SSE events.

    SSE event types:
      - text_delta   : {"delta": "..."}  — incremental text from Claude
      - thinking     : {"delta": "..."}  — incremental thinking (if enabled)
      - tool_call    : {"name": "...", "input": {...}}  — tool being called
      - tool_result  : {"name": "...", "output": "..."}  — tool result (truncated for display)
      - done         : {"session_id": "..."}  — conversation turn complete
      - error        : {"message": "..."}
    """
    try:
        while True:
            # --- Call Claude with streaming ---
            with client.messages.stream(
                model="claude-opus-4-6",
                max_tokens=16000,
                thinking={"type": "adaptive"},
                system=[
                    {
                        "type": "text",
                        "text": _SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                tools=TOOL_DEFINITIONS,
                messages=messages,
            ) as stream:
                # Collect the full response while streaming deltas
                tool_use_blocks: list[dict] = []
                current_tool: dict | None = None
                current_tool_input_json = ""

                for event in stream:
                    # --- Thinking delta ---
                    if event.type == "content_block_start":
                        if event.content_block.type == "thinking":
                            pass  # will stream via delta
                        elif event.content_block.type == "tool_use":
                            current_tool = {
                                "id": event.content_block.id,
                                "name": event.content_block.name,
                                "input": {},
                            }
                            current_tool_input_json = ""

                    elif event.type == "content_block_delta":
                        delta = event.delta
                        if delta.type == "thinking_delta":
                            yield _sse("thinking", {"delta": delta.thinking})
                        elif delta.type == "text_delta":
                            yield _sse("text_delta", {"delta": delta.text})
                        elif delta.type == "input_json_delta":
                            current_tool_input_json += delta.partial_json

                    elif event.type == "content_block_stop":
                        if current_tool is not None:
                            # Parse accumulated JSON input
                            try:
                                current_tool["input"] = json.loads(current_tool_input_json)
                            except json.JSONDecodeError:
                                current_tool["input"] = {"raw": current_tool_input_json}
                            tool_use_blocks.append(current_tool)
                            yield _sse("tool_call", {
                                "name": current_tool["name"],
                                "input": current_tool["input"],
                            })
                            current_tool = None
                            current_tool_input_json = ""

                # Get the final message to check stop_reason
                final_message = stream.get_final_message()

            # --- If Claude is done (no tool calls), finish ---
            if final_message.stop_reason != "tool_use":
                _conversations[session_id] = messages  # save history
                yield _sse("done", {"session_id": session_id})
                return

            # --- Execute all tool calls ---
            # Append Claude's assistant turn (with tool_use blocks)
            assistant_content = []
            for block in final_message.content:
                if block.type == "thinking":
                    assistant_content.append({"type": "thinking", "thinking": block.thinking, "signature": block.signature})
                elif block.type == "text":
                    assistant_content.append({"type": "text", "text": block.text})
                elif block.type == "tool_use":
                    assistant_content.append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    })

            messages.append({"role": "assistant", "content": assistant_content})

            # Build tool results turn
            tool_results = []
            for tool_block in tool_use_blocks:
                result = dispatch_tool(tool_block["name"], tool_block["input"])
                # Truncate for SSE display (full result goes to Claude)
                display_result = result if len(result) <= 500 else result[:500] + "…"
                yield _sse("tool_result", {
                    "name": tool_block["name"],
                    "output": display_result,
                })
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_block["id"],
                    "content": result,
                })

            messages.append({"role": "user", "content": tool_results})
            # loop continues → send tool results back to Claude

    except anthropic.APIError as e:
        yield _sse("error", {"message": f"API error: {e}"})
    except Exception as e:
        yield _sse("error", {"message": f"Internal error: {e}"})


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/health")
def health():
    return {"status": "ok", "model": "claude-opus-4-6"}


@app.post("/chat")
async def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())

    # Retrieve or create conversation
    messages = list(_conversations.get(session_id, []))  # copy
    messages.append({"role": "user", "content": req.message})

    async def event_stream():
        # First event: session ID so client knows the session
        yield _sse("session", {"session_id": session_id})
        async for chunk in _agent_stream(session_id, messages):
            yield chunk

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/history/{session_id}")
def get_history(session_id: str):
    if session_id not in _conversations:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "messages": _conversations[session_id]}


@app.delete("/history/{session_id}")
def clear_history(session_id: str):
    _conversations.pop(session_id, None)
    return {"status": "cleared", "session_id": session_id}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8181, reload=True)
