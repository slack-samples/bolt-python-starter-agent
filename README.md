# Starter Agent for Slack

A minimal starter template for building AI-powered Slack agents with [Bolt for Python](https://docs.slack.dev/tools/bolt-python/). Works with the [Slack MCP Server](https://github.com/slackapi/slack-mcp-server) to search messages, read channels, send messages, and manage canvases — all from within your agent. Includes one example tool (emoji reactions), giving you a clean foundation to build on.

## Choose Your Framework

This repo contains the same app built with three different AI agent frameworks. Pick the one that fits your stack:

| App | Directory | Get Started | Framework |
|-----|-----------|-------------|-----------|
| **Claude Agent SDK** | `claude-agent-sdk/` | [View README](./claude-agent-sdk/README.md) | [claude-agent-sdk](https://platform.claude.com/docs/en/agent-sdk/overview) |
| **OpenAI Agents SDK** | `openai-agents-sdk/` | [View README](./openai-agents-sdk/README.md) | [openai-agents](https://openai.github.io/openai-agents-python/) |
| **Pydantic AI** | `pydantic-ai/` | [View README](./pydantic-ai/README.md) | [pydantic-ai](https://ai.pydantic.dev/) |

All implementations share the same Slack listener layer and the same user experience. The only difference is how the agent is defined and executed under the hood.

## What It Can Do

The starter agent interacts with users through three entry points:

* **App Home** — Displays a welcome message and Slack MCP Server connection status.
* **Direct Messages** — Users message the agent directly. It responds in-thread, maintaining context across follow-ups.
* **Channel @mentions** — Mention the agent in any channel to get a response without leaving the conversation.

When connected to the [Slack MCP Server](https://github.com/slackapi/slack-mcp-server), the agent can search messages and files, read channel history and threads, send and schedule messages, and create and update canvases. The template also includes one example tool (emoji reactions). Add your own tools to customize the agent for your use case.

## Local Development

This repo uses a vendored (pre-release) build of `slack-bolt` from the [bolt-python](https://github.com/slackapi/bolt-python) `main` branch. The `.whl` file lives in `vendor/` and is referenced by each app's `requirements.txt`.

To update the vendored bolt-python to the latest `main`, run the Claude Code slash command:

```
/project:vendor-bolt
```
