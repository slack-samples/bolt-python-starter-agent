from unittest.mock import Mock

import pytest
from slack_sdk.oauth.installation_store import Installation
from vercel.blob import BlobNotFoundError

from oauth.installation_store import BlobInstallationStore


class FakeBlob:
    def __init__(self):
        self.blobs: dict[str, bytes] = {}
        self.put_options: list[dict] = []

    async def put_blob(self, pathname: str, body: bytes, **options):
        self.blobs[pathname] = body
        self.put_options.append(options)

    async def get_blob(self, pathname: str, *, access: str):
        if pathname not in self.blobs:
            raise BlobNotFoundError()
        return Mock(body=self.blobs[pathname])

    async def query_blobs(self, *, prefix: str):
        for pathname in list(self.blobs):
            if pathname.startswith(prefix):
                yield Mock(pathname=pathname)

    async def delete_blob(self, pathnames: list[str]):
        for pathname in pathnames:
            del self.blobs[pathname]


class TestBlobInstallationStore:
    def setup_method(self):
        self.fake_blob = FakeBlob()
        self.store = BlobInstallationStore(blob=self.fake_blob)

    @pytest.mark.asyncio
    async def test_saves_and_finds_bot(self):
        await self.store.async_save(
            Installation(team_id="T1", user_id="U1", bot_token="xoxb-1", bot_id="B1")
        )

        bot = await self.store.async_find_bot(enterprise_id=None, team_id="T1")

        assert bot.bot_token == "xoxb-1"
        assert sorted(self.fake_blob.blobs) == [
            "installations/none-T1/bot-latest.json",
            "installations/none-T1/installer-U1-latest.json",
            "installations/none-T1/installer-latest.json",
        ]
        assert self.fake_blob.put_options == [
            {"access": "private", "allow_overwrite": True},
            {"access": "private", "allow_overwrite": True},
            {"access": "private", "allow_overwrite": True},
        ]

    @pytest.mark.asyncio
    async def test_finds_user_installation(self):
        await self.store.async_save(
            Installation(
                team_id="T1",
                user_id="U1",
                bot_token="xoxb-1",
                user_token="xoxp-1",
            )
        )

        installation = await self.store.async_find_installation(
            enterprise_id=None, team_id="T1", user_id="U1"
        )

        assert installation.user_token == "xoxp-1"
        assert installation.bot_token == "xoxb-1"

    @pytest.mark.asyncio
    async def test_keys_enterprise_installs_by_enterprise(self):
        await self.store.async_save(
            Installation(
                enterprise_id="E1",
                user_id="U1",
                bot_token="xoxb-1",
                is_enterprise_install=True,
            )
        )

        installation = await self.store.async_find_installation(
            enterprise_id="E1", team_id="T2", is_enterprise_install=True
        )

        assert installation.bot_token == "xoxb-1"
        assert "installations/E1-none/bot-latest.json" in self.fake_blob.blobs

    @pytest.mark.asyncio
    async def test_returns_none_when_missing(self):
        bot = await self.store.async_find_bot(enterprise_id=None, team_id="T1")
        installation = await self.store.async_find_installation(
            enterprise_id=None, team_id="T1", user_id="U1"
        )

        assert bot is None
        assert installation is None

    @pytest.mark.asyncio
    async def test_deletes_installation(self):
        await self.store.async_save(
            Installation(team_id="T1", user_id="U1", bot_token="xoxb-1")
        )

        await self.store.async_delete_installation(
            enterprise_id=None, team_id="T1", user_id="U1"
        )

        assert sorted(self.fake_blob.blobs) == [
            "installations/none-T1/bot-latest.json",
            "installations/none-T1/installer-latest.json",
        ]

        await self.store.async_delete_all(enterprise_id=None, team_id="T1")

        assert self.fake_blob.blobs == {}
