from thread_context.store import SessionStore


class TestSessionStore:
    def test_keeps_different_users_in_the_same_thread_independent(self):
        store = SessionStore()
        store.set_session("C1", "T1", "U1", "sid-1")

        assert store.get_session("C1", "T1", "U2") is None

        store.set_session("C1", "T1", "U2", "sid-2")

        assert store.get_session("C1", "T1", "U1") == "sid-1"
        assert store.get_session("C1", "T1", "U2") == "sid-2"
