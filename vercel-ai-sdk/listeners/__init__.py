from slack_bolt.async_app import AsyncApp

from listeners import actions, events, views


def register_listeners(app: AsyncApp):
    actions.register(app)
    events.register(app)
    views.register(app)
