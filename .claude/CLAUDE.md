# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A monorepo containing three parallel implementations of a **Starter Agent** for Slack built with Bolt for Python. All implementations are functionally identical from the Slack user's perspective but use different AI agent frameworks:

- `claude-agent-sdk/` -- Built with **Claude Agent SDK**
- `openai-agents-sdk/` -- Built with **OpenAI Agents SDK**
- `pydantic-ai/` -- Built with **Pydantic AI**

This is a minimal starter template. It includes one example tool (emoji reactions) and optional Slack MCP Server integration.

## Commands

All commands must be run from within the respective project directory (`claude-agent-sdk/`, `openai-agents-sdk/`, or `pydantic-ai/`).

```sh
# Run the app (requires .env with OPENAI_API_KEY or ANTHROPIC_API_KEY; Slack tokens optional with CLI)
slack run          # via Slack CLI
python3 app.py     # directly

# Lint and format (CI runs these on push to main and all PRs)
ruff check .
ruff format --check .

# Run tests
pytest
```

## Monorepo Structure

```
.github/              # Shared CI workflows and dependabot config
claude-agent-sdk/    # Claude Agent SDK implementation
openai-agents-sdk/   # OpenAI Agents SDK implementation
pydantic-ai/         # Pydantic AI implementation
```

CI runs ruff lint/format checks against all directories via a matrix strategy in `.github/workflows/ruff.yml`. Dependabot monitors `requirements.txt` in all directories independently.

## Architecture (shared across all implementations)

Three-layer design: **app.py** -> **listeners/** -> **agent/**

**Entry point (`app.py`)** initializes Bolt with Socket Mode and calls `register_listeners(app)`.

**Listeners** are organized by Slack platform feature:
- `listeners/events/` -- `app_home_opened`, `app_mentioned`, `message`
- `listeners/actions/` -- `feedback_buttons`

Each sub-package has a `register(app)` function called from `listeners/__init__.py`.

**AgentDeps** (`agent/deps.py`) is a dataclass carrying `client`, `user_id`, `channel_id`, `thread_ts`. Constructed in each listener handler and passed to the agent at runtime.

**Conversation history** (`thread_context/store.py`) is a thread-safe in-memory dict keyed by `(channel_id, thread_ts)` with TTL-based cleanup. This enables multi-turn context.

**Handler flow** (DM, mention): get history from store -> run agent -> post response in thread with feedback blocks -> store updated messages.

## Key Differences Between Implementations

| Aspect | Claude Agent SDK | OpenAI Agents SDK | Pydantic AI |
|--------|-----------------|-------------------|-------------|
| Agent file | `agent/agent.py` | `agent/agent.py` | `agent/agent.py` |
| App type | `AsyncApp` (fully async) | `App` (sync) | `App` (sync) |
| Agent definition | `ClaudeSDKClient` with `ClaudeAgentOptions` | `Agent[AgentDeps](model="gpt-4.1-mini")` | `Agent(deps_type=AgentDeps)` |
| Model config | Managed by SDK (Claude models) | Set directly on agent constructor | `get_model()` selects provider at runtime (Anthropic preferred) |
| Tool definition | `@tool` decorated functions via MCP server | `@function_tool` decorated functions | Plain async functions |
| Tool context param | `args` dict (no context param) | `RunContextWrapper[AgentDeps]` | `RunContext[AgentDeps]` |
| Execution | `await run_agent(text, session_id=...)` | `Runner.run_sync(agent, input=..., context=...)` | `agent.run_sync(text, model=..., deps=..., message_history=...)` |
| Result output | `response_text` from collected `TextBlock.text` | `result.final_output` | `result.output` |
| Conversation history | Session-based via `resume` (server-side) | `list` stored locally | `list[ModelMessage]` stored locally |
| API key env var | `ANTHROPIC_API_KEY` | `OPENAI_API_KEY` | `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` |
| Feedback blocks | Native `FeedbackButtonsElement` | Native `FeedbackButtonsElement` | Native `FeedbackButtonsElement` |
