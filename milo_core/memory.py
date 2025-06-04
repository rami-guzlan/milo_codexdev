from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, List


@dataclass
class Message:
    """Represents a single chat message."""

    role: str
    content: str


class ShortTermMemory:
    """In-memory store for recent conversation messages.

    Parameters
    ----------
    max_messages:
        Maximum number of messages to retain. When the limit is
        reached, older messages are discarded.
    """

    def __init__(self, max_messages: int = 50) -> None:
        self.max_messages = max_messages
        self._messages: Deque[Message] = deque(maxlen=max_messages)

    def add_message(self, role: str, content: str) -> None:
        """Add a message to memory."""
        self._messages.append(Message(role=role, content=content))

    def get_messages(self) -> List[Message]:
        """Return a list of stored messages in chronological order."""
        return list(self._messages)

    def clear(self) -> None:
        """Remove all messages from memory."""
        self._messages.clear()

    # NOTE: Retrieval augmented generation (RAG) integration would hook into
    # this class. For example, `get_messages` could be expanded to merge
    # results from a local vector store containing long-term knowledge.
