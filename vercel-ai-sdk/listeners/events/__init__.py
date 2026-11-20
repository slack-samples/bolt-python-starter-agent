from slack_bolt.async_app import AsyncApp
from slack_bolt.context.ack.async_ack import AsyncAck

from .app_home_opened import handle_app_home_opened
from .app_mentioned import handle_app_mentioned
from .message import handle_message


async def ack_event(ack: AsyncAck):
    await ack()


def register(app: AsyncApp):
    app.event("app_home_opened")(handle_app_home_opened)
    app.event("app_mention")(ack=ack_event, lazy=[handle_app_mentioned])
    app.event("message")(ack=ack_event, lazy=[handle_message])
