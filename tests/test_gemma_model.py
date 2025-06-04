from __future__ import annotations

from unittest.mock import MagicMock, patch

from milo_core.llm.gemma import GemmaLocalModel


@patch("milo_core.llm.gemma.AutoTokenizer")
@patch("milo_core.llm.gemma.AutoModelForCausalLM")
def test_gemma_model_generation(mock_model_cls, mock_tokenizer_cls) -> None:
    mock_tokenizer = MagicMock()
    mock_tokenizer.__call__ = MagicMock(return_value={"input_ids": [[0]]})
    mock_tokenizer.decode.return_value = "hello"
    mock_tokenizer_cls.from_pretrained.return_value = mock_tokenizer

    mock_model = MagicMock()
    mock_model.generate.return_value = [[0]]
    mock_model_cls.from_pretrained.return_value = mock_model

    model = GemmaLocalModel("/tmp/model")
    model.load_model()
    out = model.generate_response("hi")
    assert out == "hello"
    mock_model.generate.assert_called_once()


@patch("milo_core.llm.gemma.TextIteratorStreamer")
@patch("milo_core.llm.gemma.AutoTokenizer")
@patch("milo_core.llm.gemma.AutoModelForCausalLM")
def test_gemma_model_stream(
    mock_model_cls, mock_tokenizer_cls, mock_streamer_cls
) -> None:
    mock_tokenizer = MagicMock()
    mock_tokenizer.__call__ = MagicMock(return_value={"input_ids": [[0]]})
    mock_tokenizer_cls.from_pretrained.return_value = mock_tokenizer
    mock_streamer = MagicMock()
    mock_streamer.__iter__.return_value = iter(["a", "b"])
    mock_streamer_cls.return_value = mock_streamer
    mock_model = MagicMock()
    mock_model.generate.side_effect = lambda **kwargs: None
    mock_model_cls.from_pretrained.return_value = mock_model

    model = GemmaLocalModel("/tmp/model")
    model.load_model()
    tokens = list(model.stream_response("hi"))
    assert tokens == ["a", "b"]
