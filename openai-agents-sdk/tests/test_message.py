import logging
from unittest.mock import Mock

from slack_bolt import BoltContext
from slack_sdk import WebClient

from listeners.events.message import handle_message
from thread_context import conversation_store

test_logger = logging.getLogger(__name__)


class TestMessage:
    def setup_method(self):
        conversation_store.set_history("C123", "1.0", [])
        self.fake_context = Mock(BoltContext)
        self.fake_context.bot_user_id = "UBOT"
        self.fake_context.channel_id = "C123"
        self.fake_context.user_id = "U123"
        self.fake_set_status = Mock(
            side_effect=RuntimeError("stop before running the agent")
        )

    def handle(self, text: str):
        handle_message(
            client=Mock(WebClient),
            context=self.fake_context,
            event={
                "channel_type": "channel",
                "text": text,
                "thread_ts": "1.0",
                "ts": "2.0",
                "user": "U123",
            },
            logger=test_logger,
            say=Mock(),
            say_stream=Mock(),
            set_status=self.fake_set_status,
        )

    def test_answers_thread_reply_in_engaged_thread(self):
        self.handle("and then?")

        self.fake_set_status.assert_called_once()

    def test_skips_thread_reply_that_mentions_the_agent(self):
        self.handle("<@UBOT> and then?")

        self.fake_set_status.assert_not_called()
