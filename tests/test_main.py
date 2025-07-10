from __future__ import annotations

from unittest.mock import patch

from milo_core.main import main


@patch("milo_core.main.converse")
@patch("milo_core.main.run_gui")
@patch("milo_core.main.HuggingFaceModel")
@patch("milo_core.main.WhisperSTT")
@patch("milo_core.main.PiperTTS")
@patch("milo_core.main.PluginManager")
@patch("milo_core.main.MemoryManager")
@patch("milo_core.main.load_config")
def test_main_starts_conversation(
    mock_load,
    mock_memory,
    mock_pm,
    mock_tts,
    mock_stt,
    mock_model,
    mock_run_gui,
    mock_converse,
) -> None:
    mock_load.return_value = {
        "llm": {"model": "my-model"},
        "gui": {"enabled": False},
        "stt": {},
        "tts": {"voice": "v"},
        "memory": {},
    }
    main()
    mock_model.assert_called_with("my-model")
    mock_model.return_value.load_model.assert_called_once()
    mock_pm.return_value.discover_plugins.assert_called_once()
    mock_memory.assert_called_with(mock_model.return_value, db_path="./milo_memory_db")
    mock_converse.assert_called_once()
    mock_run_gui.assert_not_called()
