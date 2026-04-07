from slack_bolt import App

from .feedback_buttons import handle_feedback_button


def register(app: App):
    app.action("feedback")(handle_feedback_button)
