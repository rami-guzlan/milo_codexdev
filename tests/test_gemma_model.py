from __future__ import annotations

from unittest.mock import MagicMock, patch

from milo_core.llm.gemma import GemmaLocalModel
from milo_core.memory import Message


@patch("milo_core.llm.gemma.Llama")
def test_gemma_stream(mock_llama_cls) -> None:
    mock_llama = MagicMock()
    mock_stream = [
        {"choices": [{"delta": {"content": "a"}}]},
        {"choices": [{"delta": {"content": "b"}}]},
    ]
    mock_llama.create_chat_completion.return_value = iter(mock_stream)
    mock_llama_cls.return_value = mock_llama

    model = GemmaLocalModel("model")
    history = [Message(role="user", content="hi")]
    tokens = list(model.stream_response(history))
    assert tokens == ["a", "b"]
