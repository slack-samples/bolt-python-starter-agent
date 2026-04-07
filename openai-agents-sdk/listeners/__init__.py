from slack_bolt import App

from listeners import actions, events, views


def register_listeners(app: App):
    actions.register(app)
    events.register(app)
    views.register(app)
