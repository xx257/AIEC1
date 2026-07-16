"""FastAPI backend for the codebase concierge chat app.

Serves the static chat UI and exposes the agent behind two endpoints: a plain
JSON one and a Server-Sent Events one that streams the agent's tool calls to the
browser as it works. Both share `stream_reply` — the single place the agent is
wired in.
"""

from __future__ import annotations

import json
import logging
import os
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    SystemMessage,
    ToolUseBlock,
    create_sdk_mcp_server,
    query,
    tool,
)
from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# INFO so tool calls show up in the server log — that's how you verify the agent
# actually reached for a tool rather than answering from memory.
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("concierge")

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

# The repository the agent answers questions about. Defaults to this session's
# directory so the app is useful with no configuration.
TARGET_REPO = os.environ.get("TARGET_REPO", str(BASE_DIR.parent))

SYSTEM_PROMPT = """You are a codebase concierge for the repository you are running in.
Answer questions about it accurately and concisely — a short paragraph, not an essay.
Cite the file paths you relied on. Read the code before answering; never guess.
If the repository does not contain the answer, say so."""

app = FastAPI(title="Codebase Concierge")

# Serve CSS/JS assets (index.html is served explicitly at "/" below).
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# --- Custom tool -----------------------------------------------------------


@tool("count_lines", "Count the lines in a file", {"file_path": str})
async def count_lines(args: dict[str, Any]) -> dict[str, Any]:
    """Count lines in a file, so size questions don't burn context reading it."""
    path = Path(args["file_path"])
    if not path.is_absolute():
        path = Path(TARGET_REPO) / path

    log.info("count_lines: %s", path)
    try:
        with path.open(encoding="utf-8", errors="replace") as f:
            count = sum(1 for _ in f)
    except OSError as exc:
        return {"content": [{"type": "text", "text": f"Could not read {path}: {exc}"}]}

    return {"content": [{"type": "text", "text": f"{path}: {count} lines"}]}


concierge_server = create_sdk_mcp_server(
    name="concierge", version="1.0.0", tools=[count_lines]
)


# --- The agent -------------------------------------------------------------

# Maps a browser conversation_id to the SDK session_id that backs it, so
# follow-up messages resume the same conversation instead of starting fresh.
# In-memory: conversations reset when the server restarts.
_sessions: dict[str, str] = {}


# The tools this agent may use. Read-only by design.
ALLOWED_TOOLS = ["Read", "Glob", "Grep", "mcp__concierge__count_lines"]

# The actual safety boundary. `allowed_tools` on its own does NOT stop the agent
# reaching for a tool that isn't on it — verified: it called Bash anyway. Listing
# the mutating tools here removes them from the session entirely, so no chat
# message can write to or execute on the machine.
DISALLOWED_TOOLS = [
    "Bash",
    "BashOutput",
    "KillShell",
    "Write",
    "Edit",
    "NotebookEdit",
    "WebFetch",
    "WebSearch",
    "Task",
]


def _build_options(conversation_id: str) -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        allowed_tools=ALLOWED_TOOLS,
        disallowed_tools=DISALLOWED_TOOLS,
        mcp_servers={"concierge": concierge_server},
        cwd=TARGET_REPO,
        max_turns=25,
        resume=_sessions.get(conversation_id),
    )


def _describe(block: ToolUseBlock) -> str:
    """A short human-readable label for a tool call, for the progress line."""
    args = block.input if isinstance(block.input, dict) else {}
    target = args.get("file_path") or args.get("pattern") or args.get("path")
    name = block.name.split("__")[-1]
    return f"{name} {target}" if target else name


async def stream_reply(message: str, conversation_id: str) -> AsyncIterator[dict[str, Any]]:
    """Run the agent and yield UI events as it works.

    Yields `{"type": "tool", "label": ...}` per tool call, then exactly one
    terminal `{"type": "done"|"error", "reply": ...}`. This is the seam where
    the agent is wired in — both endpoints go through here.
    """
    try:
        async for msg in query(prompt=message, options=_build_options(conversation_id)):
            if isinstance(msg, SystemMessage) and msg.subtype == "init":
                _sessions[conversation_id] = msg.data["session_id"]

            elif isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, ToolUseBlock):
                        label = _describe(block)
                        log.info("tool: %s", label)
                        yield {"type": "tool", "label": label}

            elif isinstance(msg, ResultMessage):
                _sessions[conversation_id] = msg.session_id
                if msg.is_error or not msg.result:
                    yield {
                        "type": "error",
                        "reply": "Sorry — I couldn't finish that one. Try rephrasing?",
                    }
                else:
                    yield {"type": "done", "reply": msg.result}
    except Exception:
        # An agent failure is a chat reply, not a 500.
        log.exception("agent failed")
        yield {"type": "error", "reply": "Sorry — something went wrong on my end."}


async def generate_reply(message: str, conversation_id: str) -> str:
    """Non-streaming wrapper: run the agent and return just the final text."""
    reply = "Sorry — something went wrong on my end."
    async for event in stream_reply(message, conversation_id):
        if event["type"] in ("done", "error"):
            reply = event["reply"]
    return reply


# --- Routes ----------------------------------------------------------------


class ChatRequest(BaseModel):
    message: str
    conversation_id: str


class ChatResponse(BaseModel):
    reply: str


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    reply = await generate_reply(request.message, request.conversation_id)
    return ChatResponse(reply=reply)


@app.get("/api/chat/stream")
async def chat_stream(message: str, conversation_id: str) -> StreamingResponse:
    """Same agent as /api/chat, but streams progress. GET so EventSource works."""

    async def events() -> AsyncIterator[str]:
        async for event in stream_reply(message, conversation_id):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
