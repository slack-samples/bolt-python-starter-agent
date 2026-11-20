import pytest
from vercel.cache.cache_in_memory import AsyncInMemoryCache

from oauth.state_store import RuntimeCacheOAuthStateStore


class TestRuntimeCacheOAuthStateStore:
    def setup_method(self):
        self.store = RuntimeCacheOAuthStateStore(cache=AsyncInMemoryCache())

    @pytest.mark.asyncio
    async def test_state_is_consumed_once(self):
        state = await self.store.async_issue()

        assert await self.store.async_consume(state) is True
        assert await self.store.async_consume(state) is False

    @pytest.mark.asyncio
    async def test_unknown_state_is_rejected(self):
        assert await self.store.async_consume("unknown") is False
