from __future__ import annotations

import queue
import subprocess
import threading
from typing import Iterable

import numpy as np

from .interface import SpeechToText, TextToSpeech


class WhisperSTT(SpeechToText):
    """Speech recognition using `faster-whisper` with `ffmpeg` input."""

    def __init__(
        self,
        model: str = "base",
        sample_rate: int = 16_000,
        block_size: int = 16_000,
        input_format: str = "pulse",
        input_device: str = "default",
    ) -> None:
        from faster_whisper import WhisperModel  # lazy import

        self.model = WhisperModel(model, device="cpu", compute_type="int8")
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
        segments, _ = self.model.transcribe(samples)
        return "".join(segment.text for segment in segments).strip()


class PiperTTS(TextToSpeech):
    """Text to speech engine using Piper and `ffplay` playback."""

    def __init__(self, model_path: str, config_path: str | None = None) -> None:
        try:
            from piper.voice import PiperVoice
        except ModuleNotFoundError as exc:  # pragma: no cover - optional library
            raise ImportError("piper-tts library is required for PiperTTS") from exc

        self.voice = PiperVoice.load(model_path, config_path)
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
                self._process = subprocess.Popen(
                    [
                        "ffplay",
                        "-autoexit",
                        "-nodisp",
                        "-loglevel",
                        "quiet",
                        "-f",
                        "s16le",
                        "-ar",
                        str(self.voice.config.sample_rate),
                        "-ac",
                        "1",
                        "-",
                    ],
                    stdin=subprocess.PIPE,
                )
                assert self._process.stdin is not None
                for chunk in self.voice.synthesize_stream_raw(text):
                    if self._stop_event.is_set():
                        break
                    self._process.stdin.write(chunk)
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
