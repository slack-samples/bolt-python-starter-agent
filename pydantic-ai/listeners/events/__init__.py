from slack_bolt import App

from .app_home_opened import handle_app_home_opened
from .app_mentioned import handle_app_mentioned
from .message import handle_message


def register(app: App):
    app.event("app_home_opened")(handle_app_home_opened)
    app.event("app_mention")(handle_app_mentioned)
    app.event("message")(handle_message)
