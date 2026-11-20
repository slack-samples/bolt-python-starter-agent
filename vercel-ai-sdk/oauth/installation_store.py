import json
import logging
from logging import Logger

from slack_sdk.oauth.installation_store.async_installation_store import (
    AsyncInstallationStore,
)
from slack_sdk.oauth.installation_store.models.bot import Bot
from slack_sdk.oauth.installation_store.models.installation import Installation
from vercel import blob as vercel_blob
from vercel.blob import BlobNotFoundError

logger = logging.getLogger(__name__)


class BlobInstallationStore(AsyncInstallationStore):
    """Installation store backed by private Vercel Blob storage.

    Keeps the latest bot and installer data per workspace or org, using the
    same file names as slack_sdk's FileInstallationStore.
    """

    def __init__(self, blob=vercel_blob):
        self._blob = blob

    @property
    def logger(self) -> Logger:
        return logger

    async def async_save(self, installation: Installation):
        directory = self._directory(installation.enterprise_id, installation.team_id)

        await self.async_save_bot(installation.to_bot())

        entity = json.dumps(installation.__dict__)
        await self._put(f"{directory}/installer-latest.json", entity)
        u_id = installation.user_id or "none"
        await self._put(f"{directory}/installer-{u_id}-latest.json", entity)

    async def async_save_bot(self, bot: Bot):
        if bot.bot_token is None:
            self.logger.debug(
                "Skipped saving a new row because of the absence of bot token in it"
            )
            return

        directory = self._directory(bot.enterprise_id, bot.team_id)
        await self._put(f"{directory}/bot-latest.json", json.dumps(bot.__dict__))

    async def async_find_bot(
        self,
        *,
        enterprise_id: str | None,
        team_id: str | None,
        is_enterprise_install: bool | None = False,
    ) -> Bot | None:
        if is_enterprise_install:
            team_id = None
        directory = self._directory(enterprise_id, team_id)
        data = await self._get(f"{directory}/bot-latest.json")
        if data is None:
            return None
        return Bot(**data)

    async def async_find_installation(
        self,
        *,
        enterprise_id: str | None,
        team_id: str | None,
        user_id: str | None = None,
        is_enterprise_install: bool | None = False,
    ) -> Installation | None:
        if is_enterprise_install:
            team_id = None
        directory = self._directory(enterprise_id, team_id)
        pathname = f"{directory}/installer-latest.json"
        if user_id is not None:
            pathname = f"{directory}/installer-{user_id}-latest.json"

        data = await self._get(pathname)
        if data is None:
            return None
        installation = Installation(**data)

        if user_id is not None or installation.bot_token is None:
            latest_bot = await self.async_find_bot(
                enterprise_id=enterprise_id,
                team_id=team_id,
                is_enterprise_install=is_enterprise_install,
            )
            if (
                latest_bot is not None
                and installation.bot_token != latest_bot.bot_token
            ):
                installation.bot_id = latest_bot.bot_id
                installation.bot_user_id = latest_bot.bot_user_id
                installation.bot_token = latest_bot.bot_token
                installation.bot_scopes = latest_bot.bot_scopes
                installation.bot_refresh_token = latest_bot.bot_refresh_token
                installation.bot_token_expires_at = latest_bot.bot_token_expires_at

        return installation

    async def async_delete_bot(
        self, *, enterprise_id: str | None, team_id: str | None
    ) -> None:
        directory = self._directory(enterprise_id, team_id)
        await self._delete_by_prefix(f"{directory}/bot-")

    async def async_delete_installation(
        self,
        *,
        enterprise_id: str | None,
        team_id: str | None,
        user_id: str | None = None,
    ) -> None:
        directory = self._directory(enterprise_id, team_id)
        if user_id is not None:
            await self._delete_by_prefix(f"{directory}/installer-{user_id}-")
        else:
            await self._delete_by_prefix(f"{directory}/installer-")

    @staticmethod
    def _directory(enterprise_id: str | None, team_id: str | None) -> str:
        return f"installations/{enterprise_id or 'none'}-{team_id or 'none'}"

    async def _put(self, pathname: str, entity: str) -> None:
        await self._blob.put_blob(
            pathname,
            entity.encode(),
            access="private",
            allow_overwrite=True,
        )

    async def _get(self, pathname: str) -> dict | None:
        try:
            result = await self._blob.get_blob(pathname, access="private")
        except BlobNotFoundError:
            self.logger.debug(f"Installation data missing: {pathname}")
            return None
        return json.loads(result.body)

    async def _delete_by_prefix(self, prefix: str) -> None:
        pathnames = [
            blob.pathname async for blob in self._blob.query_blobs(prefix=prefix)
        ]
        if pathnames:
            await self._blob.delete_blob(pathnames)
