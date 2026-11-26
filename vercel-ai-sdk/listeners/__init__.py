from slack_bolt.async_app import AsyncApp

from listeners import actions, events


def register_listeners(app: AsyncApp):
    actions.register(app)
    events.register(app)
