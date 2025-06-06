from __future__ import annotations

import queue
import subprocess
import threading
import time
from typing import Iterable

import numpy as np
import pyaudio
import torch

from .interface import SpeechToText, TextToSpeech


class WhisperSTT(SpeechToText):
    """Speech recognition using `faster-whisper` with a VAD microphone stream."""

    def __init__(
        self,
        model: str = "base",
        sample_rate: int = 16_000,
        block_size: int = 16_000,
        input_format: str = "pulse",
        input_device: str = "default",
        vad_threshold: float = 0.5,
        vad_silence_duration: float = 0.8,
    ) -> None:
        from faster_whisper import WhisperModel  # lazy import

        self.model = WhisperModel(model, device="cpu", compute_type="int8")
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.input_format = input_format
        self.input_device = input_device
        self.vad_threshold = vad_threshold
        self.vad_silence_duration = vad_silence_duration

        self.vad_model, vad_utils = torch.hub.load(
            "snakers4/silero-vad",
            "silero_vad",
            trust_repo=True,
        )
        (
            self.get_speech_timestamps,
            _,
            self.read_audio,
            _,
            self.collect_chunks,
        ) = vad_utils

    def listen(self) -> str:
        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.block_size,
            input_device_index=None,
        )

        audio_chunks: list[np.ndarray] = []
        silence_start: float | None = None
        speech_detected = False

        try:
            while True:
                data = stream.read(self.block_size, exception_on_overflow=False)
                samples = np.frombuffer(data, dtype=np.float32)
                speech_prob = self.vad_model(
                    torch.from_numpy(samples), self.sample_rate
                ).item()
                if speech_prob > self.vad_threshold:
                    speech_detected = True
                    silence_start = None
                    audio_chunks.append(samples)
                elif speech_detected:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start >= self.vad_silence_duration:
                        break
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()

        if not audio_chunks:
            return ""

        audio = np.concatenate(audio_chunks)
        segments, _ = self.model.transcribe(audio)
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
