from __future__ import annotations

import queue
import threading
from typing import Iterable

import numpy as np
import sounddevice as sd

from .interface import SpeechToText, TextToSpeech


class WhisperSTT(SpeechToText):
    """Speech recognition using ``whisper`` with ``sounddevice`` input."""

    def __init__(
        self, model: str = "base", sample_rate: int = 16_000, block_size: int = 16_000
    ) -> None:
        from whisper import load_model  # lazy import

        self.model = load_model(model)
        self.sample_rate = sample_rate
        self.block_size = block_size

    def listen(self) -> str:
        audio = sd.rec(
            self.block_size, samplerate=self.sample_rate, channels=1, dtype="float32"
        )
        sd.wait()
        samples = np.squeeze(audio)
        result = self.model.transcribe(samples, fp16=False)
        return result.get("text", "")


class CoquiTTS(TextToSpeech):
    """Text to speech engine using ``Coqui TTS`` and ``sounddevice`` playback."""

    def __init__(
        self, model_name: str = "tts_models/en/ljspeech/tacotron2-DDC"
    ) -> None:
        try:
            from TTS.api import TTS as Coqui
        except ModuleNotFoundError as exc:  # pragma: no cover - library optional
            raise ImportError("Coqui TTS library is required for CoquiTTS") from exc

        self.tts = Coqui(model_name)
        self._queue: queue.Queue[str] = queue.Queue()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while True:
            text = self._queue.get()
            if text is None:  # type: ignore[comparison-overlap]
                break
            if not self._stop_event.is_set():
                audio = self.tts.tts(text)
                sd.play(audio, samplerate=self.tts.synthesizer.output_sample_rate)
                sd.wait()
            self._queue.task_done()
            self._stop_event.clear()

    def speak(self, tokens: Iterable[str]) -> None:
        for token in tokens:
            if self._stop_event.is_set():
                break
            self._queue.put(token)

    def stop(self) -> None:
        self._stop_event.set()
        sd.stop()
