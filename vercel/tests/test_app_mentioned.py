import logging
from unittest.mock import AsyncMock, Mock, patch

import ai
import pytest
import pytest_asyncio
from slack_bolt.context.async_context import AsyncBoltContext
from slack_sdk.web.async_client import AsyncWebClient

from listeners.events.app_mentioned import handle_app_mentioned
from thread_context import conversation_store

test_logger = logging.getLogger(__name__)

FIRST_HISTORY = [ai.user_message("look into this"), ai.assistant_message("On it")]
SECOND_HISTORY = [ai.user_message("what did you find?"), ai.assistant_message("Hi")]


class TestAppMentioned:
    @pytest_asyncio.fixture(autouse=True)
    async def setup_history(self):
        await conversation_store.set_history("C234", "1.0", "U123", FIRST_HISTORY)

    def setup_method(self):
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
            AsyncMock(return_value=("Hi", SECOND_HISTORY)),
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

        assert fake_run_agent.call_args.kwargs["message_history"] is None
        assert (
            await conversation_store.get_history("C234", "1.0", "U456")
            == SECOND_HISTORY
        )
        assert (
            await conversation_store.get_history("C234", "1.0", "U123") == FIRST_HISTORY
        )
