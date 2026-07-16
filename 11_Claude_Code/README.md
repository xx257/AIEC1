# Session 11: Claude Code & the Claude Agent SDK


| 📰 Session Sheet                                                                                                                                               | ⏺️ Recording                                                                                                                                           | 🖼️ Slides                                              | 👨‍💻 Repo                                                                                                                                                   | 📝 Homework                                                                                                                                 | 📁 Feedback                                         |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| [Session 11: Claude Code & Claude Agent SDK](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_Docs/Modules/11_Claude_Code) | [Recording!](https://us02web.zoom.us/rec/share/2I5HA6DwVFgmtyjPaq1SJDgkaVEuYZoWYyMCK8DOAZ99Zm6f7dTi0IGONXj6mRel.YHFzKF03mI5v6JAM) passcode: `&Qhi!cf0` | [Session 11 Slides](https://canva.link/uw1cl42x84tm6zh) | You are here! [Certification Challenge](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_Docs/Certification%20Challenge) | [Optional Session 11 Assignment](https://forms.gle/sAyr5BgBLTfgJV8EA) [Cert Challenge Submission Form](https://forms.gle/xtM9F38nfRKcdjH97) | [Feedback 7/7](https://forms.gle/oDrguLDNvva65mtM8) |


## Useful Resources

**Claude Code**

- [Claude Code Documentation](https://code.claude.com/docs) — official docs: setup, workflows, settings
- [Claude Code Quickstart](https://code.claude.com/docs/en/quickstart) — from install to first session
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) — Anthropic engineering guide

**Claude Agent SDK**

- [Agent SDK Overview](https://docs.anthropic.com/en/api/agent-sdk/overview) — what the SDK is and when to use it
- [Building Agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) — Anthropic engineering deep dive

## Main Assignment

**Build a chat web app powered by the Claude Agent SDK** — and build it *with* Claude Code.

This session is markdown-only on purpose. There is no starter code and no notebook: every line of code in your final app will be written in collaboration with Claude Code. The session has one build arc across a single breakout room:

```text
you → Claude Code → chat app skeleton → wire in Agent SDK query()
      (FastAPI + chat UI, echo stub)      ├─ tools: Read / Glob / Grep
                                           └─ your custom tool
```

The finished product: a **codebase concierge** — a chat interface in the browser where an agent (with real tools) answers questions about any repository you point it at. In Session 10 you served models behind endpoints; today you serve an *agent* behind one.

Work through the three guides in order:

```text
01_Installing_Claude_Code.md   # install, authenticate, verify
02_Using_Claude_Code.md        # drive Claude Code; scaffold the chat app skeleton
03_Claude_Agent_SDK.md         # add the agent and connect it to your website
```

## Outline

### Breakout Room #1: Claude Code, the Agent SDK, and the Connection

- Task 1: Install Claude Code and authenticate ([guide](./01_Installing_Claude_Code.md))
- Task 2: Learn the loop — explore a repo you didn't write ([guide](./02_Using_Claude_Code.md))
- Task 3: Scaffold the chat app skeleton with Claude Code (plan → implement → verify)
- Task 4: Write the project's `CLAUDE.md`
- Question #1 and Question #2
- Task 5: Install the Agent SDK and run your first `query()` ([guide](./03_Claude_Agent_SDK.md))
- Task 6: Wire the agent into `/api/chat` — replace the echo stub
- Task 7: Conversation memory — resume sessions across messages
- Task 8: Give the agent a custom tool
- Question #3 and Question #4
- Activity #1: Level Up the Chat App

## Questions

### ❓ Question #1

While scaffolding in Task 3 you used **plan mode** before letting Claude Code write anything. Why does an agent that can execute shell commands need a permission system at all, and why is plan mode particularly valuable when starting a project from an empty directory?

#### ✅ Answer

A shell command can make real changes, while an LLM response is just text. If Claude gives a bad answer, I can ignore it and ask again. But if it deletes files, overwrites code, or runs the wrong command, those changes happen immediately. The permission system is there because the model doesn’t actually know whether its actions are correct, so a human still needs to approve anything that could affect the real environment.

Plan mode is especially useful when starting from an empty directory because there are no constraints yet. In an existing project, the codebase, folder structure, and tests help guide decisions. In a new project, the first few choices often become the foundation for everything that comes later.

### ❓ Question #2

`CLAUDE.md` is loaded into context at the start of every session. What belongs in it — and what *doesn't*? How does this relate to what you learned about context management and memory in Session 3?

#### ✅ Answer

`CLAUDE.md` should contain information that Claude can’t easily learn from reading the code itself. Things like how to run the project, required environment variables, important architectural decisions, or project-specific rules are good candidates. In my project, I included notes about where the agent logic lives and some tool-related behavior that isn’t obvious from a quick scan of the codebase.

What doesn’t belong is information that can already be found in the code, long explanations, or notes that are unlikely to affect future work. Since the file is loaded into every session, every line takes up context that could be used for solving the actual task.

This connects closely to Session 3’s discussion of context management and memory. `CLAUDE.md`is more like retrieval than memory. Instead of trying to remember everything, it should contain only the small amount of information that’s consistently useful across sessions. The goal is to provide the right context, not the most context. One thing I learned while working on the assignment is that stale context can be dangerous. At one point, my `CLAUDE.md` still described the original echo stub after I had already replaced it. Claude trusted the note and incorrectly assumed the stub was still there. That experience reinforced that outdated context can be worse than no context at all, because the model may treat it as an authoritative source.

### ❓ Question #3

The Agent SDK gives you the same agent loop that powers Claude Code. Compare this to the agent loops you hand-built with LangGraph in Sessions 2–4: what does the SDK give you for free, and what control do you give up?

#### ✅ Answer

The biggest thing the Agent SDK gives me for free is the entire agent loop. In Sessions 2-4, I had to build and manage that loop myself with LangGraph: model calls, tool execution, state management, memory, and all the logic that keeps the agent running. With the Agent SDK, most of that is already built in. For example, session memory only required creating a session and passing the session ID back in future requests, whereas in LangGraph I had to explicitly manage state and persistence myself.

The tradeoff is that I have less visibility and control over what happens inside the loop. With LangGraph, I could see every step, add custom logic between model and tool calls, branch based on state, or design completely different workflows. With the Agent SDK, I mostly provide the prompt, tools, and configuration, then let the SDK handle the execution flow.

### ❓ Question #4

Your chat app could have called a chat completions API directly, the way you did early in the course. What do you gain by routing every message through the Agent SDK's `query()` instead — and what new risks does an agent with tools introduce that a plain chat completion doesn't have? How did your tool allowlist and permission mode address them?

#### ✅ Answer

By routing messages through the Agent SDK’s `query()` instead of calling a chat completions API directly, the agent can actively gather information instead of relying only on the context I provide. Earlier in the course, if I wanted the model to answer questions about a codebase, I had to manually select and paste the relevant files. With the Agent SDK, the agent can search the repository, read files, and retrieve the information it needs before generating a response. That makes the answers more grounded and scalable.

The tradeoff is that an agent with tools can take actions, not just generate text. A normal chat completion can give a bad answer, but an agent can potentially run commands or use tools in ways I didn’t intend. Since my chat app accepts user input, I need to think about what actions the agent is allowed to perform, not just what answers it generates.

I addressed that risk by restricting the agent to read-only capabilities and removing any tools that could modify the environment. During testing, I discovered that `allowed_tools` is only an auto-approval list, not a true security boundary. The agent could still attempt to call tools that were not on that listI even saw it reach for `Bash`. The real protection is actually coming from `disallowed_tools`, which removes tools such as `Bash`, `Write`, `Edit`, and `WebFetch` from the session entirely. That means the model cannot execute shell commands, modify files, or access the network, even if prompted by a user message or instructions hidden in a file it reads. I also left the permission mode at the SDK default because this application runs headlessly on a server. Since there is no human available to approve tool calls at runtime, the safety guarantees need to come from the tool configuration itself rather than interactive approval prompts.

## Activity 1: Level Up the Chat App

Extend your working chat app with **at least one** of the following (built with Claude Code, of course):

1. **Live progress streaming** — stream the agent's activity to the browser (e.g. via Server-Sent Events) so users see tool calls ("reading `app.py`…") while the agent works, instead of a spinner
2. **Multi-conversation support** — a sidebar of separate conversations, each mapped to its own SDK session
3. **A second custom tool** — something genuinely useful for your target repo (e.g. `git_log` for recent changes, or a test-runner summary tool)

Whichever you pick, demo it in your Loom video and explain the design decision in one paragraph.

- **Live progress streaming**

I added streaming because real requests against my repository often took 7–15 seconds, and a loading spinner doesn't tell the user whether the agent is working or the request has stalled. Since `query()` already streams tool calls as the agent works, I used Server-Sent Events (SSE) to surface that progress in the UI. I chose SSE over WebSockets because the communication is one-way and only lasts for a single request, and `EventSource` is built into the browser so it required no extra dependencies. The main tradeoff is that `EventSource` only supports GET requests, so the message has to be passed through the query string instead of a JSON body. I kept the original `POST /api/chat` endpoint for testing with curl and as a fallback, and both routes use the same`stream_reply()` function so the agent logic remains in one place.

## Advanced Activity: The Cat Shop Concierge

Connect your Session 8 cat shop MCP server to your chat app's agent via the SDK's `mcp_servers` option. Your chat app becomes a shopping concierge: users can browse the catalog, fill a cart, and check out — in natural language, through the UI you built, hitting the OAuth-protected server you wrote in Session 8.

Include your findings and a demo in your Loom video.

## Ship 🚢

The working chat app!

### Deliverables

- A short Loom showing:
  - Claude Code scaffolding or extending the app (plan → implement → verify — show the plan!); and
  - the chat app answering real questions about a repository, including at least one visible custom-tool use

## Share 🚀

Make a social media post about your final application!

### Deliverables

- Make a post on any social media platform about what you built!

Here's a template to get you started:

```
🚀 Exciting News! 🚀

I am thrilled to announce that I have just built and shipped a chat app powered by the Claude Agent SDK — scaffolded entirely with Claude Code! 🎉🤖

🔍 Three Key Takeaways:
1️⃣
2️⃣
3️⃣

Let's continue pushing the boundaries of what's possible in the world of AI agents. Here's to many more innovations! 🚀
Shout out to @AIMakerspace !

#ClaudeCode #AgentSDK #AIAgents #Innovation #AI #TechMilestone

Feel free to reach out if you're curious or would like to collaborate on similar projects! 🤝🔥
```

## Submitting Your Homework (Optional For Extra Mark)

Follow these steps to prepare and submit your homework:

1. Pull the latest updates from upstream into the main branch of your repo:

```bash
git checkout main
git pull upstream main
git push origin main
```

1. Work through `01_Installing_Claude_Code.md`, `02_Using_Claude_Code.md`, and `03_Claude_Agent_SDK.md` in order.
2. Build your chat app in a new `chat-app/` folder inside this session directory (include its `CLAUDE.md` — we want to see it!).
3. Fill in your answers to Questions #1–#4 in this README.
4. Complete Activity #1 and record your Loom video.
5. Add, commit, and push your work to your origin repository. Remove `.env` files and API keys before committing.

When submitting your homework, provide the GitHub URL to your repo.