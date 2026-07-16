# Codebase Concierge

A chat web app powered by the **Claude Agent SDK**: a **FastAPI** backend serving a
plain HTML/CSS/JS chat UI, with a read-only agent behind it that answers questions
about a repository. Ask it "what does this repo do?" and it reads the code and tells
you, citing file paths.

Tool calls stream to the browser over Server-Sent Events, so you see the agent
working ("Read main.py…") instead of a spinner.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- An `ANTHROPIC_API_KEY`

## Run

```bash
uv sync
export ANTHROPIC_API_KEY="sk-ant-..."
uv run uvicorn main:app --reload
```

Then open http://127.0.0.1:8000 and ask about the repo.

### Configuration

| Variable | Default | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Required. The agent won't run without it. |
| `TARGET_REPO` | the parent directory (`11_Claude_Code/`) | Absolute path of the repo the agent answers questions about. |

Point it at any repo you like:

```bash
TARGET_REPO=/path/to/some/repo uv run uvicorn main:app --reload
```

## Project layout

```
chat-app/
  main.py            # FastAPI app: routes, agent options, custom tool
  static/
    index.html       # chat UI markup
    style.css        # chat UI styling
    app.js           # EventSource against /api/chat/stream, renders the conversation
  pyproject.toml     # uv project + dependencies
```

## API

`GET /api/chat/stream?message=...&conversation_id=...` — Server-Sent Events. This is
what the UI uses. Each event is a JSON object:

```
data: {"type": "tool", "label": "Read main.py"}
data: {"type": "done", "reply": "This repo is ..."}
```

`POST /api/chat` — the same agent, non-streaming. Handy for curl:

```json
// request
{ "message": "what does this repo do?", "conversation_id": "abc-123" }

// response
{ "reply": "This repo is ..." }
```

## How it works

- **The seam.** All agent logic is in `stream_reply()` in [`main.py`](main.py). Both
  routes go through it.
- **Memory.** Each browser `conversation_id` maps to an SDK `session_id`, replayed via
  `resume=`, so follow-up questions understand "it". In-memory — resets on restart.
- **A custom tool.** `count_lines` is exposed to the agent as an in-process MCP server,
  so size questions don't burn context reading whole files.
- **Read-only.** The agent gets `Read`, `Glob`, `Grep`, and `count_lines`. Note that
  `allowed_tools` is only an auto-approve list — it does *not* block anything on its
  own. `DISALLOWED_TOOLS` in `main.py` is what actually removes `Bash`/`Write`/`Edit`
  from the session, and it's the reason a chat message can't touch the filesystem.
