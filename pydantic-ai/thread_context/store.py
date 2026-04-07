import threading
import time

from pydantic_ai.messages import ModelMessage


class ConversationStore:
    """Thread-safe in-memory conversation history store.

    Stores Pydantic AI message histories keyed by (channel_id, thread_ts).
    Includes TTL-based cleanup and a maximum conversation limit.
    """

    def __init__(self, ttl_seconds: int = 86400, max_conversations: int = 1000):
        self._store: dict[tuple[str, str], dict] = {}
        self._lock = threading.Lock()
        self._ttl_seconds = ttl_seconds
        self._max_conversations = max_conversations

    def get_history(self, channel_id: str, thread_ts: str) -> list[ModelMessage] | None:
        """Retrieve conversation history for a thread.

        Returns None if no history exists or if the history has expired.
        """
        key = (channel_id, thread_ts)
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            if time.time() - entry["timestamp"] > self._ttl_seconds:
                del self._store[key]
                return None
            return entry["messages"]

    def set_history(
        self, channel_id: str, thread_ts: str, messages: list[ModelMessage]
    ) -> None:
        """Store conversation history for a thread."""
        key = (channel_id, thread_ts)
        with self._lock:
            self._store[key] = {
                "messages": messages,
                "timestamp": time.time(),
            }
            self._cleanup()

    def _cleanup(self) -> None:
        """Remove expired entries and enforce max conversation limit."""
        now = time.time()

        expired = [
            k
            for k, v in self._store.items()
            if now - v["timestamp"] > self._ttl_seconds
        ]
        for k in expired:
            del self._store[k]

        if len(self._store) > self._max_conversations:
            sorted_keys = sorted(
                self._store.keys(), key=lambda k: self._store[k]["timestamp"]
            )
            for k in sorted_keys[: len(self._store) - self._max_conversations]:
                del self._store[k]
