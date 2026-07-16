# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv sync                                   # install/refresh dependencies
export ANTHROPIC_API_KEY="sk-ant-..."     # required — the agent will not run without it
uv run uvicorn main:app --reload          # run dev server at http://127.0.0.1:8000
```

`TARGET_REPO` sets the repo the agent answers questions about; it defaults to this
session directory (`11_Claude_Code/`). There is no test suite or linter configured.

Smoke test:

```bash
curl -X POST localhost:8000/api/chat -H 'Content-Type: application/json' \
  -d '{"message":"what does this repo do?","conversation_id":"t1"}'
```

## Architecture

A "codebase concierge": a Claude Agent SDK agent behind a FastAPI backend and a
static, framework-free frontend.

- **`main.py`** — the FastAPI app. `GET /` serves `static/index.html`; `/static` is
  mounted for CSS/JS; `POST /api/chat` takes `{message, conversation_id}` → `{reply}`;
  `GET /api/chat/stream` is the same agent over Server-Sent Events.
- **`static/app.js`** — the frontend. Generates one `conversation_id` per page load and
  opens an `EventSource` against `/api/chat/stream`, rendering tool calls live.

### `stream_reply` (the seam)

All agent logic lives in `async def stream_reply(message, conversation_id)`. It wraps the
SDK's `query()` and yields UI events: zero or more `{"type": "tool", "label": ...}`, then
exactly one terminal `{"type": "done"|"error", "reply": ...}`. Both routes go through it —
`generate_reply` just drains it for the final string. Agent failures become an `error`
event, never a 500.

### Two things that are easy to get wrong

- **`allowed_tools` does not restrict anything on its own.** It's an auto-approve list;
  the agent will still call a tool that isn't on it (verified: it reached for `Bash`).
  `DISALLOWED_TOOLS` is what actually makes this agent read-only. Don't drop it.
- **Conversation memory** is the `_sessions` dict mapping `conversation_id` → SDK
  `session_id`, passed back via `resume=`. In-memory, so it resets on restart.
