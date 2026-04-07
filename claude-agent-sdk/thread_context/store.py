import threading
import time


class SessionStore:
    """Thread-safe in-memory session ID store.

    Stores Claude Agent SDK session IDs keyed by (channel_id, thread_ts).
    The SDK manages conversation history server-side via sessions, so we
    only need to track session IDs for resuming conversations.
    Includes TTL-based cleanup and a maximum entry limit.
    """

    def __init__(self, ttl_seconds: int = 86400, max_entries: int = 1000):
        self._store: dict[tuple[str, str], dict] = {}
        self._lock = threading.Lock()
        self._ttl_seconds = ttl_seconds
        self._max_entries = max_entries

    def get_session(self, channel_id: str, thread_ts: str) -> str | None:
        """Retrieve session ID for a thread.

        Returns None if no session exists or if the session has expired.
        """
        key = (channel_id, thread_ts)
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            if time.time() - entry["timestamp"] > self._ttl_seconds:
                del self._store[key]
                return None
            return entry["session_id"]

    def set_session(self, channel_id: str, thread_ts: str, session_id: str) -> None:
        """Store session ID for a thread."""
        key = (channel_id, thread_ts)
        with self._lock:
            self._store[key] = {
                "session_id": session_id,
                "timestamp": time.time(),
            }
            self._cleanup()

    def _cleanup(self) -> None:
        """Remove expired entries and enforce max entry limit."""
        now = time.time()

        expired = [
            k
            for k, v in self._store.items()
            if now - v["timestamp"] > self._ttl_seconds
        ]
        for k in expired:
            del self._store[k]

        if len(self._store) > self._max_entries:
            sorted_keys = sorted(
                self._store.keys(), key=lambda k: self._store[k]["timestamp"]
            )
            for k in sorted_keys[: len(self._store) - self._max_entries]:
                del self._store[k]
