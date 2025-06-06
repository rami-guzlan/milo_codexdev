from __future__ import annotations

from typing import Protocol, Any, Iterator, List

from milo_core.memory import Message


class LocalModelInterface(Protocol):
    """Protocol for local LLM implementations."""

    def load_model(self, *args: Any, **kwargs: Any) -> None:
        """Load the model into memory."""
        ...

    def generate_response(self, prompt: str, *args: Any, **kwargs: Any) -> str:
        """Generate a text response for the given prompt."""
        ...

    def stream_response(
        self, history: List[Message], *args: Any, **kwargs: Any
    ) -> Iterator[str]:
        """Yield tokens for the generated response based on chat history."""
        ...

    def unload(self) -> None:
        """Release any resources held by the model."""
        ...


class StubLocalModel:
    """Basic stub implementation that raises ``NotImplementedError``."""

    def load_model(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError("Local model loading is not implemented")

    def generate_response(self, prompt: str, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError("Response generation is not implemented")

    def stream_response(
        self, history: List[Message], *args: Any, **kwargs: Any
    ) -> Iterator[str]:
        raise NotImplementedError("Streaming is not implemented")

    def unload(self) -> None:
        raise NotImplementedError("Local model unload is not implemented")
