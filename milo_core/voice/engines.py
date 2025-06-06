from __future__ import annotations

import queue
import threading
import subprocess
from typing import Iterable

import numpy as np

from .interface import SpeechToText, TextToSpeech


class WhisperSTT(SpeechToText):
    """Speech recognition using ``whisper`` with ``ffmpeg`` input."""

    def __init__(
        self,
        model: str = "base",
        sample_rate: int = 16_000,
        block_size: int = 16_000,
        input_format: str = "pulse",
        input_device: str = "default",
    ) -> None:
        from whisper import load_model  # lazy import

        self.model = load_model(model)
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.input_format = input_format
        self.input_device = input_device

    def listen(self) -> str:
        duration = self.block_size / self.sample_rate
        proc = subprocess.run(
            [
                "ffmpeg",
                "-nostdin",
                "-loglevel",
                "quiet",
                "-f",
                self.input_format,
                "-i",
                self.input_device,
                "-t",
                str(duration),
                "-ar",
                str(self.sample_rate),
                "-ac",
                "1",
                "-f",
                "f32le",
                "-",
            ],
            stdout=subprocess.PIPE,
            check=False,
        )
        samples = np.frombuffer(proc.stdout, dtype=np.float32)
        result = self.model.transcribe(samples, fp16=False)
        return result.get("text", "")


class CoquiTTS(TextToSpeech):
    """Text to speech engine using ``Coqui TTS`` and ``ffplay`` playback."""

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
        self._process: subprocess.Popen | None = None
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while True:
            text = self._queue.get()
            if text is None:  # type: ignore[comparison-overlap]
                break
            if not self._stop_event.is_set():
                audio = self.tts.tts(text)
                self._process = subprocess.Popen(
                    [
                        "ffplay",
                        "-autoexit",
                        "-nodisp",
                        "-loglevel",
                        "quiet",
                        "-f",
                        "f32le",
                        "-ar",
                        str(self.tts.synthesizer.output_sample_rate),
                        "-ac",
                        "1",
                        "-",
                    ],
                    stdin=subprocess.PIPE,
                )
                assert self._process.stdin is not None
                self._process.stdin.write(audio.astype(np.float32).tobytes())
                self._process.stdin.close()
                self._process.wait()
            self._queue.task_done()
            self._stop_event.clear()

    def speak(self, tokens: Iterable[str]) -> None:
        for token in tokens:
            if self._stop_event.is_set():
                break
            self._queue.put(token)

    def stop(self) -> None:
        self._stop_event.set()
        if self._process and self._process.poll() is None:
            self._process.terminate()
            self._process = None
