# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

See the root `../.claude/CLAUDE.md` for monorepo-wide architecture, commands, and a comparison of all implementations.

## OpenAI Agents SDK Specifics

**Agent (`agent/agent.py`)** is an `Agent[AgentDeps]` with the model set directly on the agent (`model="gpt-4.1-mini"`). Tools are `@function_tool`-decorated async functions, each in its own file under `agent/tools/`. Execution uses `Runner.run_sync(agent, input=..., context=deps)`.

**Conversation history** is stored as a generic `list` and must be manually combined with new user input before passing to `Runner.run_sync()`: `input_items = history + [{"role": "user", "content": text}]`. After execution, `result.to_input_list()` is stored back.

**Feedback blocks** use the native `FeedbackButtonsElement` from `slack_sdk.models.blocks`. A single `feedback` action ID is registered.