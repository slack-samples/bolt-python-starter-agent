import logging
import time
from logging import Logger
from uuid import uuid4

from slack_sdk.oauth.state_store.async_state_store import AsyncOAuthStateStore
from vercel.cache.types import AsyncCache
from vercel.functions import AsyncRuntimeCache

logger = logging.getLogger(__name__)


class RuntimeCacheOAuthStateStore(AsyncOAuthStateStore):
    """OAuth state store backed by Vercel Runtime Cache.

    Each state can be consumed once before it expires.
    """

    def __init__(
        self,
        cache: AsyncCache | None = None,
        expiration_seconds: int = 600,
    ):
        if cache is None:
            cache = AsyncRuntimeCache(namespace="oauth-state")
        self._cache = cache
        self.expiration_seconds = expiration_seconds

    @property
    def logger(self) -> Logger:
        return logger

    async def async_issue(self, *args, **kwargs) -> str:
        state = str(uuid4())
        await self._cache.set(state, time.time(), {"ttl": self.expiration_seconds})
        return state

    async def async_consume(self, state: str) -> bool:
        created = await self._cache.get(state)
        if created is None:
            self.logger.warning(
                f"Failed to find any persistent data for state: {state}"
            )
            return False
        await self._cache.delete(state)
        return time.time() < created + self.expiration_seconds
