from milo_core.memory import ConversationMemory


def test_add_and_retrieve_messages():
    memory = ConversationMemory(max_messages=5)
    memory.add_message("user", "Hello")
    memory.add_message("assistant", "Hi")

    messages = memory.get_messages()
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[0].content == "Hello"
    assert messages[1].role == "assistant"
    assert messages[1].content == "Hi"


def test_max_messages_limit():
    memory = ConversationMemory(max_messages=2)
    memory.add_message("user", "one")
    memory.add_message("assistant", "two")
    memory.add_message("user", "three")

    messages = memory.get_messages()
    assert len(messages) == 2
    assert messages[0].content == "two"
    assert messages[1].content == "three"
