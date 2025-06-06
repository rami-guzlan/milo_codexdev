from __future__ import annotations

from pathlib import Path
from typing import Iterator, List

from llama_cpp import Llama

from .interface import LocalModelInterface
from milo_core.memory import Message


class GemmaLocalModel(LocalModelInterface):
    """Load and interact with a local Gemma GGUF model using llama.cpp."""

    def __init__(self, model_path: str | Path) -> None:
        self.model_path = str(model_path)
        # n_gpu_layers=-1 attempts to offload all possible layers to the GPU
        self.model = Llama(model_path=self.model_path, n_gpu_layers=-1, verbose=False)

    def stream_response(
        self, history: List[Message], max_new_tokens: int = 256
    ) -> Iterator[str]:
        """Yield tokens for the generated response based on chat history."""
        dict_history = [{"role": msg.role, "content": msg.content} for msg in history]
        stream = self.model.create_chat_completion(
            messages=dict_history, max_tokens=max_new_tokens, stream=True
        )
        for output in stream:
            content = output["choices"][0]["delta"].get("content")
            if content:
                yield content

    def load_model(self) -> None:  # noqa: D401 - kept for interface compatibility
        """Load the model. llama-cpp-python loads in __init__."""
        return None

    def unload(self) -> None:  # noqa: D401 - kept for interface compatibility
        """Unload the model (handled by llama-cpp-python)."""
        return None
