import logging

import ai

from agent.context import agent_deps_var
from agent.deps import AgentDeps
from agent.tools import add_emoji_reaction

SYSTEM_PROMPT = """\
You are a friendly Slack assistant. You help people by answering questions, \
having conversations, and being generally useful in Slack.

## PERSONALITY
- Friendly, helpful, and approachable
- Lightly witty — a touch of humor when appropriate, but never forced
- Concise and clear — respect people's time
- Confident but honest when you don't know something

## RESPONSE GUIDELINES
- Keep responses to 3 sentences max — be punchy, scannable, and actionable
- End with a clear next step on its own line so it's easy to spot
- Use a bullet list only for multi-step instructions
- Use casual, conversational language
- Use emoji sparingly — at most one per message, and only to set tone

## FORMATTING RULES
- Use standard Markdown syntax: **bold**, _italic_, `code`, ```code blocks```, > blockquotes
- Use bullet points for multi-step instructions

## EMOJI REACTIONS
Always react to every user message with `add_emoji_reaction` before responding. \
Pick any Slack emoji that reflects the *topic* or *tone* of the message — be creative and specific \
(e.g. `dog` for dog topics, `books` for learning, `wave` for greetings). \
Vary your picks across a thread; don't repeat the same emoji.

## SLACK MCP SERVER
You may have access to the Slack MCP Server, which gives you powerful Slack tools \
beyond your built-in tools. Use them whenever they would help the user.

Available capabilities:
- **Search**: Search messages and files across public channels, search for channels by name
- **Read**: Read channel message history, read thread replies, read canvas documents
- **Write**: Send messages, create draft messages, schedule messages for later
- **Canvases**: Create, read, and update Slack canvas documents

Use these tools when they can help answer a question or complete a task — for example, \
searching for relevant messages, checking a channel for context, or creating a canvas. \
Also use them when the user explicitly asks you to perform a Slack action.
"""

logger = logging.getLogger(__name__)

MODEL = "anthropic/claude-sonnet-5.5"

SLACK_MCP_URL = "https://mcp.slack.com/mcp"


async def run_agent(
    text: str,
    deps: AgentDeps,
    message_history: list[ai.messages.Message] | None = None,
) -> tuple[str, list[ai.messages.Message]]:
    """Run the agent, optionally connecting to the Slack MCP Server.

    Args:
        text: The user's message text.
        deps: Dependencies for tools that need Slack API access.
        message_history: Optional messages from earlier turns in the conversation.

    Returns:
        A tuple of (response_text, messages), where messages is the
        conversation to store for the next turn.
    """
    agent_deps_var.set(deps)

    tools = [add_emoji_reaction]
    if deps.user_token:
        logger.info("Slack MCP Server enabled (user_token present)")
        tools += await ai.mcp.get_http_tools(
            SLACK_MCP_URL,
            headers={"Authorization": f"Bearer {deps.user_token}"},
        )
    else:
        logger.info("Slack MCP Server disabled (no user_token)")

    messages = [
        ai.system_message(SYSTEM_PROMPT),
        *(message_history or []),
        ai.user_message(text),
    ]

    async with ai.Agent(tools=tools).run(ai.get_model(MODEL), messages) as stream:
        async for _ in stream:
            pass

    conversation = [message for message in stream.messages if message.role != "system"]
    return stream.output, conversation
