from slack_bolt.async_app import AsyncApp

from listeners import register_listeners
from listeners.events.app_mentioned import handle_app_mentioned
from listeners.events.message import handle_message


def test_registers_long_listeners_as_lazy():
    app = AsyncApp(token="xoxb-test", signing_secret="test-secret")

    register_listeners(app)

    lazy_functions = [
        function
        for listener in app._async_listeners
        for function in listener.lazy_functions
    ]
    assert lazy_functions == [handle_app_mentioned, handle_message]
