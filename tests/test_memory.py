from __future__ import annotations

from milo_core.memory import Message, ShortTermMemory


def test_add_and_retrieve_messages() -> None:
    memory = ShortTermMemory(max_messages=3)
    memory.add_message("user", "hello")
    memory.add_message("assistant", "hi")
    assert memory.get_messages() == [
        Message(role="user", content="hello"),
        Message(role="assistant", content="hi"),
    ]


def test_memory_discards_old_messages_when_full() -> None:
    memory = ShortTermMemory(max_messages=2)
    memory.add_message("user", "one")
    memory.add_message("assistant", "two")
    memory.add_message("user", "three")
    messages = memory.get_messages()
    assert len(messages) == 2
    assert messages[0].content == "two"
    assert messages[1].content == "three"


def test_clear_memory() -> None:
    memory = ShortTermMemory()
    memory.add_message("user", "foo")
    memory.clear()
    assert memory.get_messages() == []
