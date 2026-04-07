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
        self.fake_context = Mock(AsyncBoltContext)
        self.fake_context.user_id = "U123"

    @pytest.mark.asyncio
    async def test_publishes_home_view(self):
        await handle_app_home_opened(
            client=self.fake_client,
            context=self.fake_context,
            logger=test_logger,
        )

        self.fake_client.views_publish.assert_called_once()
        kwargs = self.fake_client.views_publish.call_args.kwargs
        assert kwargs["user_id"] == "U123"
        assert kwargs["view"]["type"] == "home"

    @pytest.mark.asyncio
    async def test_views_publish_exception(self, caplog):
        self.fake_client.views_publish.side_effect = Exception("test exception")

        await handle_app_home_opened(
            client=self.fake_client,
            context=self.fake_context,
            logger=test_logger,
        )

        self.fake_client.views_publish.assert_called_once()
        assert "test exception" in caplog.text
