from unittest.mock import AsyncMock, Mock, patch

import pytest
from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient

from agent.context import agent_deps_var
from agent.deps import AgentDeps
from agent.tools import add_emoji_reaction


class TestEmojiReaction:
    def setup_method(self):
        self.fake_client = Mock(AsyncWebClient)
        self.fake_client.reactions_add = AsyncMock()
        agent_deps_var.set(
            AgentDeps(
                client=self.fake_client,
                user_id="U1",
                channel_id="C1",
                thread_ts="1.0",
                message_ts="2.0",
            )
        )

    @pytest.mark.asyncio
    async def test_reacts_with_emoji(self):
        with patch("agent.tools.emoji_reaction.random.random", return_value=0.5):
            result = await add_emoji_reaction.fn("tada")

        self.fake_client.reactions_add.assert_awaited_once_with(
            channel="C1", timestamp="2.0", name="tada"
        )
        assert result == "Reacted with :tada:"

    @pytest.mark.asyncio
    async def test_skips_some_reactions(self):
        with patch("agent.tools.emoji_reaction.random.random", return_value=0.1):
            result = await add_emoji_reaction.fn("tada")

        self.fake_client.reactions_add.assert_not_called()
        assert result.startswith("Skipped :tada:")

    @pytest.mark.asyncio
    async def test_reports_reaction_error(self):
        self.fake_client.reactions_add.side_effect = SlackApiError(
            "already_reacted", {"ok": False, "error": "already_reacted"}
        )

        with patch("agent.tools.emoji_reaction.random.random", return_value=0.5):
            result = await add_emoji_reaction.fn("tada")

        assert result == "Could not add reaction: already_reacted"
