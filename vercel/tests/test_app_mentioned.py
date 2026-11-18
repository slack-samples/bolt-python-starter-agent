import logging
from unittest.mock import AsyncMock, Mock, patch

import pytest
from slack_bolt.context.async_context import AsyncBoltContext
from slack_sdk.web.async_client import AsyncWebClient

from listeners.events.app_mentioned import handle_app_mentioned
from thread_context import session_store

test_logger = logging.getLogger(__name__)


class TestAppMentioned:
    def setup_method(self):
        session_store.set_session("C234", "1.0", "U123", "session-1")
        self.fake_client = Mock(AsyncWebClient)
        self.fake_client.reactions_add = AsyncMock()
        self.fake_context = Mock(AsyncBoltContext)
        self.fake_context.bot_user_id = "UBOT"
        self.fake_context.channel_id = "C234"
        self.fake_context.user_id = "U456"

    @pytest.mark.asyncio
    async def test_starts_a_separate_session_for_a_second_person_in_the_thread(self):
        with patch(
            "listeners.events.app_mentioned.run_agent",
            AsyncMock(return_value=("Hi", "session-2")),
        ) as fake_run_agent:
            await handle_app_mentioned(
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
                say=AsyncMock(),
                say_stream=AsyncMock(
                    return_value=Mock(append=AsyncMock(), stop=AsyncMock())
                ),
                set_status=AsyncMock(),
            )

        assert fake_run_agent.call_args.kwargs["session_id"] is None
        assert session_store.get_session("C234", "1.0", "U456") == "session-2"
        assert session_store.get_session("C234", "1.0", "U123") == "session-1"
