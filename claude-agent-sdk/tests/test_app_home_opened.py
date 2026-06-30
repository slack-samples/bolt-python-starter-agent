import logging
from unittest.mock import AsyncMock, Mock

import pytest
from slack_bolt.context.async_context import AsyncBoltContext
from slack_sdk.web.async_client import AsyncWebClient

from listeners.events.app_home_opened import handle_app_home_opened

test_logger = logging.getLogger(__name__)


class TestAppHomeOpened:
    def setup_method(self):
        self.fake_client = Mock(AsyncWebClient)
        self.fake_client.views_publish = AsyncMock()
        self.fake_client.assistant_threads_setSuggestedPrompts = AsyncMock()
        self.fake_context = Mock(AsyncBoltContext)
        self.fake_context.user_id = "U123"

    @pytest.mark.asyncio
    async def test_publishes_home_view_when_tab_is_home(self):
        await handle_app_home_opened(
            client=self.fake_client,
            event={"tab": "home", "channel": "D123"},
            context=self.fake_context,
            logger=test_logger,
        )

        self.fake_client.views_publish.assert_called_once()
        kwargs = self.fake_client.views_publish.call_args.kwargs
        assert kwargs["user_id"] == "U123"
        assert kwargs["view"]["type"] == "home"
        self.fake_client.assistant_threads_setSuggestedPrompts.assert_not_called()

    @pytest.mark.asyncio
    async def test_sets_suggested_prompts_when_tab_is_messages(self):
        await handle_app_home_opened(
            client=self.fake_client,
            event={"tab": "messages", "channel": "D123"},
            context=self.fake_context,
            logger=test_logger,
        )

        self.fake_client.assistant_threads_setSuggestedPrompts.assert_called_once()
        kwargs = self.fake_client.assistant_threads_setSuggestedPrompts.call_args.kwargs
        assert kwargs["channel_id"] == "D123"
        assert isinstance(kwargs["prompts"], list)
        self.fake_client.views_publish.assert_not_called()

    @pytest.mark.asyncio
    async def test_views_publish_exception(self, caplog):
        self.fake_client.views_publish.side_effect = Exception("test exception")

        await handle_app_home_opened(
            client=self.fake_client,
            event={"tab": "home", "channel": "D123"},
            context=self.fake_context,
            logger=test_logger,
        )

        self.fake_client.views_publish.assert_called_once()
        assert "test exception" in caplog.text
