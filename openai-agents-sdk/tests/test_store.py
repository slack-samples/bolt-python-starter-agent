from thread_context.store import ConversationStore


class TestConversationStore:
    def test_keeps_different_users_in_the_same_thread_independent(self):
        store = ConversationStore()
        store.set_history("C1", "T1", "U1", [{"role": "user", "content": "a"}])

        assert store.get_history("C1", "T1", "U2") is None

        store.set_history("C1", "T1", "U2", [{"role": "user", "content": "b"}])

        assert store.get_history("C1", "T1", "U1") == [{"role": "user", "content": "a"}]
        assert store.get_history("C1", "T1", "U2") == [{"role": "user", "content": "b"}]
