import ai
from vercel.cache.types import AsyncCache
from vercel.functions import AsyncRuntimeCache


class ConversationStore:
    """Conversation history store backed by Vercel Runtime Cache.

    Falls back to an in-memory cache outside of Vercel. Messages are stored
    as JSON and expire after the TTL.
    """

    def __init__(self, cache: AsyncCache | None = None, ttl_seconds: int = 86400):
        if cache is None:
            cache = AsyncRuntimeCache(namespace="thread-context")
        self._cache = cache
        self._ttl_seconds = ttl_seconds

    async def get_history(
        self, channel_id: str, thread_ts: str, user_id: str
    ) -> list[ai.messages.Message] | None:
        """Retrieve conversation history for a thread.

        Returns None if no history exists or if the history has expired.
        """
        stored = await self._cache.get(f"{channel_id}:{thread_ts}:{user_id}")
        if stored is None:
            return None
        return [ai.messages.Message.model_validate(message) for message in stored]

    async def set_history(
        self,
        channel_id: str,
        thread_ts: str,
        user_id: str,
        messages: list[ai.messages.Message],
    ) -> None:
        """Store conversation history for a thread."""
        await self._cache.set(
            f"{channel_id}:{thread_ts}:{user_id}",
            [message.model_dump(mode="json") for message in messages],
            {"ttl": self._ttl_seconds},
        )
