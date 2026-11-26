import logging
from unittest.mock import AsyncMock, Mock, patch

import ai
import pytest
import pytest_asyncio
from slack_bolt.context.async_context import AsyncBoltContext
from slack_sdk.web.async_client import AsyncWebClient

from listeners.events.message import handle_message
from thread_context import conversation_store

test_logger = logging.getLogger(__name__)

EARLIER_HISTORY = [ai.user_message("hello"), ai.assistant_message("Hi")]
UPDATED_HISTORY = [*EARLIER_HISTORY, ai.user_message("and then?")]


class TestMessage:
    @pytest_asyncio.fixture(autouse=True)
    async def setup_history(self):
        await conversation_store.set_history("C123", "1.0", "U123", EARLIER_HISTORY)

    def setup_method(self):
        self.fake_client = Mock(AsyncWebClient)
        self.fake_client.reactions_add = AsyncMock()
        self.fake_context = Mock(AsyncBoltContext)
        self.fake_context.bot_user_id = "UBOT"
        self.fake_context.channel_id = "C123"
        self.fake_context.user_id = "U123"

    async def handle(self, text: str, **event: str | None) -> AsyncMock:
        with patch(
            "listeners.events.message.run_agent", AsyncMock(side_effect=RuntimeError)
        ) as fake_run_agent:
            await handle_message(
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
                say=AsyncMock(),
                say_stream=Mock(),
                set_status=AsyncMock(),
            )
        return fake_run_agent

    @pytest.mark.asyncio
    async def test_runs_agent_for_thread_reply_in_engaged_thread(self):
        fake_run_agent = await self.handle("and then?")

        fake_run_agent.assert_called_once()

    @pytest.mark.asyncio
    async def test_skips_thread_reply_that_mentions_the_agent(self):
        fake_run_agent = await self.handle("<@UBOT> and then?")

        fake_run_agent.assert_not_called()

    @pytest.mark.asyncio
    async def test_runs_agent_for_dm_that_mentions_the_agent(self):
        self.fake_context.channel_id = "D123"

        fake_run_agent = await self.handle(
            "<@UBOT> help", channel_type="im", thread_ts=None, ts="3.0"
        )

        fake_run_agent.assert_called_once()

    @pytest.mark.asyncio
    async def test_skips_thread_reply_from_someone_without_their_own_session(self):
        self.fake_context.user_id = "U456"

        fake_run_agent = await self.handle("what did you find?", user="U456")

        fake_run_agent.assert_not_called()

    @pytest.mark.asyncio
    async def test_stores_the_new_session_under_the_person_who_replied(self):
        await conversation_store.set_history("C123", "1.0", "U123", EARLIER_HISTORY)

        with patch(
            "listeners.events.message.run_agent",
            AsyncMock(return_value=("Hi", UPDATED_HISTORY)),
        ):
            await handle_message(
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
                say=AsyncMock(),
                say_stream=AsyncMock(
                    return_value=Mock(append=AsyncMock(), stop=AsyncMock())
                ),
                set_status=AsyncMock(),
            )

        assert (
            await conversation_store.get_history("C123", "1.0", "U123")
            == UPDATED_HISTORY
        )
        assert await conversation_store.get_history("C123", "1.0", "U456") is None
