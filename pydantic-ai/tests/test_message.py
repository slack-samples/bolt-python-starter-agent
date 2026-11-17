import logging
from unittest.mock import Mock, patch

from slack_bolt import BoltContext
from slack_sdk import WebClient

from listeners.events.message import handle_message
from thread_context import conversation_store

test_logger = logging.getLogger(__name__)


class TestMessage:
    def setup_method(self):
        conversation_store.set_history("C123", "1.0", "U123", [])
        self.fake_client = Mock(WebClient)
        self.fake_client.reactions_add = Mock()
        self.fake_context = Mock(BoltContext)
        self.fake_context.bot_user_id = "UBOT"
        self.fake_context.channel_id = "C123"
        self.fake_context.user_id = "U123"

    def handle(self, text: str, **event: str | None) -> Mock:
        with patch(
            "listeners.events.message.run_agent", Mock(side_effect=RuntimeError)
        ) as fake_run_agent:
            handle_message(
                client=self.fake_client,
                context=self.fake_context,
                event={
                    "channel_type": "channel",
                    "text": text,
                    "thread_ts": "1.0",
                    "ts": "2.0",
                    "user": "U123",
                    **event,
                },
                logger=test_logger,
                say=Mock(),
                say_stream=Mock(),
                set_status=Mock(),
            )
        return fake_run_agent

    def test_runs_agent_for_thread_reply_in_engaged_thread(self):
        fake_run_agent = self.handle("and then?")

        fake_run_agent.assert_called_once()

    def test_skips_thread_reply_that_mentions_the_agent(self):
        fake_run_agent = self.handle("<@UBOT> and then?")

        fake_run_agent.assert_not_called()

    def test_runs_agent_for_dm_that_mentions_the_agent(self):
        self.fake_context.channel_id = "D123"

        fake_run_agent = self.handle(
            "<@UBOT> help", channel_type="im", thread_ts=None, ts="3.0"
        )

        fake_run_agent.assert_called_once()

    def test_skips_thread_reply_from_someone_without_their_own_session(self):
        self.fake_context.user_id = "U456"

        fake_run_agent = self.handle("what did you find?", user="U456")

        fake_run_agent.assert_not_called()

    def test_stores_the_new_session_under_the_person_who_replied(self):
        conversation_store.set_history("C123", "1.0", "U123", ["first"])

        with patch(
            "listeners.events.message.run_agent",
            Mock(
                return_value=Mock(
                    output="Hi", all_messages=Mock(return_value=["second"])
                )
            ),
        ):
            handle_message(
                client=self.fake_client,
                context=self.fake_context,
                event={
                    "channel_type": "channel",
                    "text": "and then?",
                    "thread_ts": "1.0",
                    "ts": "2.0",
                    "user": "U123",
                },
                logger=test_logger,
                say=Mock(),
                say_stream=Mock(),
                set_status=Mock(),
            )

        assert conversation_store.get_history("C123", "1.0", "U123") == ["second"]
        assert conversation_store.get_history("C123", "1.0", "U456") is None
