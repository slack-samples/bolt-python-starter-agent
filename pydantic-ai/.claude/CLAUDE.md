# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

See the root `../.claude/CLAUDE.md` for monorepo-wide architecture, commands, and a comparison of all implementations.

## Pydantic AI Specifics

**Agent (`agent/agent.py`)** is a Pydantic AI `Agent` with `deps_type=AgentDeps`. The model is **not** set on the agent (to avoid import-time client creation); instead `get_model()` selects the provider at runtime based on available API keys (`ANTHROPIC_API_KEY` preferred over `OPENAI_API_KEY`) and is passed at each `run_sync()` call site. Tools are passed via the `tools=[]` constructor parameter (not decorators) so each tool lives in its own file under `agent/tools/`.

**Conversation history** stores `list[ModelMessage]` from Pydantic AI and is passed directly as `message_history=` to `run_sync()`.

**Feedback blocks** use the native `FeedbackButtonsElement` from `slack_sdk.models.blocks`. A single `feedback` action ID is registered.