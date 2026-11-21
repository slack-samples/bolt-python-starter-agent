import json
from unittest.mock import AsyncMock, Mock

import ai
import pytest
from vercel.cache.cache_in_memory import AsyncInMemoryCache

from thread_context.store import ConversationStore


class TestConversationStore:
    @pytest.mark.asyncio
    async def test_stores_and_retrieves_history(self):
        cache = AsyncInMemoryCache()
        store = ConversationStore(cache=cache)
        messages = [ai.user_message("hello"), ai.assistant_message("hi")]

        await store.set_history("C1", "T1", "U1", messages)
        stored = await cache.get("C1:T1:U1")

        assert json.loads(json.dumps(stored)) == stored
        assert await store.get_history("C1", "T1", "U1") == messages

    @pytest.mark.asyncio
    async def test_returns_none_for_missing_key(self):
        store = ConversationStore(cache=AsyncInMemoryCache())

        assert await store.get_history("C1", "T1", "U1") is None

    @pytest.mark.asyncio
    async def test_keeps_threads_independent(self):
        store = ConversationStore(cache=AsyncInMemoryCache())
        await store.set_history("C1", "T1", "U1", [ai.user_message("a")])

        assert await store.get_history("C1", "T2", "U1") is None

    @pytest.mark.asyncio
    async def test_keeps_different_users_in_the_same_thread_independent(self):
        store = ConversationStore(cache=AsyncInMemoryCache())
        first = [ai.user_message("a")]
        second = [ai.user_message("b")]
        await store.set_history("C1", "T1", "U1", first)

        assert await store.get_history("C1", "T1", "U2") is None

        await store.set_history("C1", "T1", "U2", second)

        assert await store.get_history("C1", "T1", "U1") == first
        assert await store.get_history("C1", "T1", "U2") == second

    @pytest.mark.asyncio
    async def test_passes_ttl(self):
        cache = Mock(AsyncInMemoryCache)
        cache.set = AsyncMock()
        store = ConversationStore(cache=cache)

        await store.set_history("C1", "T1", "U1", [])

        cache.set.assert_awaited_once_with("C1:T1:U1", [], {"ttl": 86400})
