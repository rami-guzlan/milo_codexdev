from __future__ import annotations

from unittest.mock import MagicMock, patch

from milo_core.llm.huggingface import HuggingFaceModel
from milo_core.memory import Message


@patch("milo_core.llm.huggingface.TextIteratorStreamer", return_value=iter(["a", "b"]))
@patch("milo_core.llm.huggingface.AutoModelForCausalLM")
@patch("milo_core.llm.huggingface.AutoTokenizer")
def test_hf_stream(mock_tokenizer_cls, mock_model_cls, mock_streamer) -> None:
    mock_tokenizer = MagicMock()
    mock_tokenizer.apply_chat_template.return_value = "prompt"

    class TokenOut(dict):
        def to(self, device):
            return self

    mock_tokenizer.__call__ = MagicMock(return_value=TokenOut({"input_ids": [[0]]}))
    mock_tokenizer_cls.from_pretrained.return_value = mock_tokenizer

    mock_model = MagicMock()
    mock_model.generate.return_value = None
    mock_model_cls.from_pretrained.return_value = mock_model

    model = HuggingFaceModel("model")
    history = [Message(role="user", content="hi")]
    tokens = list(model.stream_response(history))
    assert tokens == ["a", "b"]
