from slack_bolt.async_app import AsyncApp

from .feedback_buttons import handle_feedback_button


def register(app: AsyncApp):
    app.action("feedback")(handle_feedback_button)
