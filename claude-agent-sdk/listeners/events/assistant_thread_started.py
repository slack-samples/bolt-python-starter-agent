from logging import Logger

from slack_bolt.context.set_suggested_prompts.async_set_suggested_prompts import (
    AsyncSetSuggestedPrompts,
)

SUGGESTED_PROMPTS = [
    {"title": "Write a Message", "message": "Help me draft a message to my team"},
    {"title": "Summarize", "message": "Can you help me summarize something?"},
    {"title": "Brainstorm", "message": "I need help brainstorming ideas"},
]


async def handle_assistant_thread_started(
    set_suggested_prompts: AsyncSetSuggestedPrompts, logger: Logger
):
    """Handle assistant thread started events by setting suggested prompts."""
    try:
        await set_suggested_prompts(
            prompts=SUGGESTED_PROMPTS,
            title="How can I help you today?",
        )
    except Exception as e:
        logger.exception(f"Failed to handle assistant thread started: {e}")
