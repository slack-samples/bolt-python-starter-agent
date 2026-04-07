from logging import Logger

from slack_bolt import Ack, BoltContext
from slack_sdk import WebClient


def handle_feedback_button(
    ack: Ack, body: dict, client: WebClient, context: BoltContext, logger: Logger
):
    """Handle thumbs up/down feedback on agent responses."""
    ack()

    try:
        channel_id = context.channel_id
        user_id = context.user_id
        message_ts = body["message"]["ts"]
        feedback_value = body["actions"][0]["value"]

        if feedback_value == "good-feedback":
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                thread_ts=message_ts,
                text="Glad that was helpful! :tada:",
            )
        else:
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                thread_ts=message_ts,
                text="Sorry that wasn't helpful. :slightly_frowning_face: Try rephrasing your question and I'll give it another shot.",
            )

        logger.debug(
            f"Feedback received: value={feedback_value}, message_ts={message_ts}"
        )
    except Exception as e:
        logger.exception(f"Failed to handle feedback: {e}")
