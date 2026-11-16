import logging
from unittest.mock import Mock, patch

from slack_bolt import BoltContext
from slack_sdk import WebClient

from listeners.events.app_mentioned import handle_app_mentioned
from thread_context import conversation_store

test_logger = logging.getLogger(__name__)


class TestAppMentioned:
    def setup_method(self):
        conversation_store.set_history("C234", "1.0", "U123", ["first"])
        self.fake_client = Mock(WebClient)
        self.fake_client.reactions_add = Mock()
        self.fake_context = Mock(BoltContext)
        self.fake_context.bot_user_id = "UBOT"
        self.fake_context.channel_id = "C234"
        self.fake_context.user_id = "U456"

    def test_starts_a_separate_session_for_a_second_person_in_the_thread(self):
        with patch(
            "listeners.events.app_mentioned.run_agent",
            Mock(
                return_value=Mock(
                    final_output="Hi", to_input_list=Mock(return_value=["second"])
                )
            ),
        ) as fake_run_agent:
            handle_app_mentioned(
                client=self.fake_client,
                context=self.fake_context,
                event={
                    "channel": "C234",
                    "text": "<@UBOT> what did you find?",
                    "thread_ts": "1.0",
                    "ts": "3.0",
                    "user": "U456",
                },
                logger=test_logger,
                say=Mock(),
                say_stream=Mock(),
                set_status=Mock(),
            )

        assert fake_run_agent.call_args.args[0] == "what did you find?"
        assert conversation_store.get_history("C234", "1.0", "U456") == ["second"]
        assert conversation_store.get_history("C234", "1.0", "U123") == ["first"]
