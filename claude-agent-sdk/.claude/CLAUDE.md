# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

See the root `../.claude/CLAUDE.md` for monorepo-wide architecture, commands, and a comparison of all implementations.

## Claude Agent SDK Specifics

**App (`app.py`)** uses `AsyncApp` from Bolt for Python. All listeners and Slack API calls are fully async (`await`).

**Agent (`agent/agent.py`)** uses `ClaudeSDKClient` from the Claude Agent SDK. Tools are registered via `create_sdk_mcp_server()` and passed as `mcp_servers` in `ClaudeAgentOptions`. The `run_agent()` function is async and returns `(response_text, session_id)`.

**Tools (`agent/tools/`)** are defined with the `@tool` decorator from `claude_agent_sdk`. One example tool (emoji reaction) is included. Tools are registered into a single MCP server via `create_sdk_mcp_server()`.

**Conversation history** is managed server-side by the Claude Agent SDK via sessions. The local `SessionStore` (`thread_context/store.py`) only maps `(channel_id, thread_ts)` to session IDs. Sessions are resumed via `ClaudeAgentOptions(resume=session_id)`.

**Feedback blocks** use the native `FeedbackButtonsElement` from `slack_sdk.models.blocks`. A single `feedback` action ID is registered.

**Dependencies** (`agent/deps.py`) use `AsyncWebClient` from `slack_sdk.web.async_client` instead of the sync `WebClient`.
