import logging
from unittest.mock import AsyncMock, Mock

import pytest
from slack_bolt.context.async_context import AsyncBoltContext
from slack_sdk.web.async_client import AsyncWebClient

from listeners.events.message import handle_message
from thread_context import session_store

test_logger = logging.getLogger(__name__)


class TestMessage:
    def setup_method(self):
        session_store.set_session("C123", "1.0", "session-1")
        self.fake_context = Mock(AsyncBoltContext)
        self.fake_context.bot_user_id = "UBOT"
        self.fake_context.channel_id = "C123"
        self.fake_context.user_id = "U123"
        self.fake_set_status = AsyncMock(
            side_effect=RuntimeError("stop before running the agent")
        )

    async def handle(self, text: str):
        await handle_message(
            client=Mock(AsyncWebClient),
            context=self.fake_context,
            event={
                "channel_type": "channel",
                "text": text,
                "thread_ts": "1.0",
                "ts": "2.0",
                "user": "U123",
            },
            logger=test_logger,
            say=AsyncMock(),
            say_stream=Mock(),
            set_status=self.fake_set_status,
        )

    @pytest.mark.asyncio
    async def test_answers_thread_reply_in_engaged_thread(self):
        await self.handle("and then?")

        self.fake_set_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_skips_thread_reply_that_mentions_the_agent(self):
        await self.handle("<@UBOT> and then?")

        self.fake_set_status.assert_not_called()
