from __future__ import annotations

from unittest.mock import patch

from milo_core.main import main


@patch("milo_core.main.converse")
@patch("milo_core.main.GemmaLocalModel")
@patch("milo_core.main.WhisperSTT")
@patch("milo_core.main.CoquiTTS")
@patch("milo_core.main.PluginManager")
@patch("milo_core.memory_manager.MemoryManager")
def test_main_starts_conversation(
    mock_memory,
    mock_pm,
    mock_tts,
    mock_stt,
    mock_model,
    mock_converse,
) -> None:
    main(["--no-gui"])
    mock_model.assert_called_with("models/gemma-3-4b-it")
    mock_model.return_value.load_model.assert_called_once()
    mock_pm.return_value.discover_plugins.assert_called_once()
    mock_memory.assert_called_with(mock_model.return_value)
    mock_converse.assert_called_once()
