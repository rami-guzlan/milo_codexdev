import argparse
from typing import List

from milo_core.llm.gemma import GemmaLocalModel
from milo_core.plugin_manager import PluginManager
from milo_core.voice.conversation import converse
from milo_core.voice.engines import WhisperSTT, PiperTTS


def build_parser() -> argparse.ArgumentParser:
    """Create and return the CLI argument parser."""
    parser = argparse.ArgumentParser(description="Run the MILO voice assistant")
    parser.add_argument(
        "--model-dir",
        default="models/gemma-3-4b-it",
        help="Path to the local model directory",
    )
    parser.add_argument(
        "--vad-threshold",
        type=float,
        default=0.5,
        help="Speech probability threshold for voice activity detection",
    )
    parser.add_argument(
        "--vad-silence-duration",
        type=float,
        default=0.8,
        help="Seconds of silence that mark the end of an utterance",
    )
    return parser


def run(args: argparse.Namespace) -> None:
    """Initialize components and start the conversation loop."""
    model = GemmaLocalModel(args.model_dir)
    model.load_model()

    stt = WhisperSTT(
        vad_threshold=args.vad_threshold,
        vad_silence_duration=args.vad_silence_duration,
    )
    tts = PiperTTS("./piper-voice.onnx")

    from milo_core.memory_manager import MemoryManager

    memory_manager = MemoryManager(model)

    pm = PluginManager()
    pm.discover_plugins()

    try:
        converse(model, stt, tts, memory_manager)
    except KeyboardInterrupt:
        pass
    finally:
        model.unload()


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    run(args)


if __name__ == "__main__":  # pragma: no cover - entry point
    main()
