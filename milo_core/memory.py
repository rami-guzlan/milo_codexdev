from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class Message:
    """Represents a single conversational message."""

    role: str
    content: str


class ConversationMemory:
    """Simple in-memory store for recent conversation history.

    This class keeps messages in memory for short-term context. Integration
    with a Retrieval Augmented Generation (RAG) system can be added later by
    extending ``add_message`` to also persist messages to a local knowledge
    base and augment retrieval in ``get_messages``.
    """

    def __init__(self, max_messages: int = 20) -> None:
        self.max_messages = max_messages
        self._messages: List[Message] = []

    def add_message(self, role: str, content: str) -> None:
        """Add a new message to memory, trimming if necessary."""
        self._messages.append(Message(role=role, content=content))
        if len(self._messages) > self.max_messages:
            # Keep only the most recent ``max_messages``
            self._messages = self._messages[-self.max_messages :]

        # Placeholder for future RAG integration.
        # A hook here would store ``content`` in a local vector database
        # for retrieval-augmented responses.

    def get_messages(self, limit: int | None = None) -> List[Message]:
        """Retrieve the most recent messages up to ``limit``."""
        if limit is None or limit > len(self._messages):
            return list(self._messages)
        return self._messages[-limit:]
