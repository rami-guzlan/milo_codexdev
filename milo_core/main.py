from __future__ import annotations

from typing import Any, Dict

from milo_core.config import load_config
from milo_core.llm import HuggingFaceModel
from milo_core.plugin_manager import PluginManager
from milo_core.voice.conversation import converse
from milo_core.voice.engines import WhisperSTT, PiperTTS
from milo_core.gui import run_gui

from milo_core.memory_manager import MemoryManager


def run(config: Dict[str, Any]) -> None:
    """Initialize components and start the conversation loop."""
    model = HuggingFaceModel(config["llm"]["model"])
    model.load_model()

    stt_cfg = config.get("stt", {})
    stt = WhisperSTT(
        model=stt_cfg.get("model", "base"),
        sample_rate=stt_cfg.get("sample_rate", 16_000),
        block_size=stt_cfg.get("block_size", 480),
        vad_silence_duration=stt_cfg.get("vad_silence_duration", 0.8),
        vad_mode=stt_cfg.get("vad_mode", 2),
    )

    tts_cfg = config.get("tts", {})
    tts = PiperTTS(tts_cfg.get("voice", ""))

    memory_cfg = config.get("memory", {})
    memory_manager = MemoryManager(
        model, db_path=memory_cfg.get("db_path", "./milo_memory_db")
    )
    memory_manager.consolidate_memories()

    pm = PluginManager()
    pm.discover_plugins()

    try:
        if not config.get("gui", {}).get("enabled", True):
            converse(model, stt, tts, memory_manager)
        else:
            run_gui(model, stt, tts, memory_manager)
    except KeyboardInterrupt:  # pragma: no cover - allow graceful exit
        pass
    finally:
        model.unload()


def main(config_path: str | None = None) -> None:
    config = load_config(config_path) if config_path else load_config()
    run(config)


if __name__ == "__main__":  # pragma: no cover - entry point
    main()
