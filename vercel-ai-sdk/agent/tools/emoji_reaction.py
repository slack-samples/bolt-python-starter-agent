import random

import ai
from slack_sdk.errors import SlackApiError

from agent.context import agent_deps_var


@ai.tool
async def add_emoji_reaction(emoji_name: str) -> str:
    """Add an emoji reaction to the user's current message to acknowledge the topic.

    Use any standard Slack emoji that matches the topic or tone of the message.
    Be creative and specific — if someone mentions a dog, use `dog`; if they sound
    frustrated, use `sweat_smile`. The examples below are common picks, not the full set:
    - Gratitude/praise: pray, bow, blush, sparkles, star-struck, heart
    - Frustration/confusion: thinking_face, face_with_monocle, sweat_smile, upside_down_face
    - Something broken: wrench, hammer_and_wrench, mag
    - Performance/slow: hourglass_flowing_sand, snail
    - Urgency: rotating_light, zap, fire
    - Success/celebration: tada, raised_hands, partying_face, rocket, muscle
    - Setup/config: gear, package
    - Network/connectivity: satellite, signal_strength
    - Agreement/acknowledgment: thumbsup, ok_hand, saluting_face, +1

    Args:
        emoji_name: The Slack emoji name without colons (e.g. 'tada', 'wrench', 'pray').
    """
    deps = agent_deps_var.get()

    # Skip ~15% of reactions to feel more natural
    if random.random() < 0.15:
        return (
            f"Skipped :{emoji_name}: reaction (randomly omitted to avoid over-reacting)"
        )

    try:
        await deps.client.reactions_add(
            channel=deps.channel_id,
            timestamp=deps.message_ts,
            name=emoji_name,
        )
        return f"Reacted with :{emoji_name}:"
    except SlackApiError as e:
        return f"Could not add reaction: {e.response['error']}"
