from __future__ import annotations

import queue
import threading
import time
from typing import Iterable

import numpy as np
import sounddevice as sd
import wave
import webrtcvad

from .interface import SpeechToText, TextToSpeech


class WhisperSTT(SpeechToText):
    """Speech recognition using `faster-whisper` with a WebRTC VAD microphone stream."""

    def __init__(
        self,
        model: str = "base",
        sample_rate: int = 16_000,
        block_size: int = 480,
        input_format: str = "pulse",
        input_device: str = "default",
        vad_silence_duration: float = 0.8,
        vad_mode: int = 2,
    ) -> None:
        from faster_whisper import WhisperModel  # lazy import

        self.model = WhisperModel(model, device="cpu", compute_type="int8")
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.input_format = input_format
        self.input_device = input_device
        self.vad_silence_duration = vad_silence_duration
        self.vad = webrtcvad.Vad(vad_mode)

    def listen(self) -> str:
        stream = sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=self.block_size,
            channels=1,
            dtype="int16",
        )
        stream.start()

        audio_chunks: list[bytes] = []
        silence_start: float | None = None
        speech_detected = False

        try:
            while True:
                data, _ = stream.read(self.block_size)
                is_speech = self.vad.is_speech(data, self.sample_rate)
                if is_speech:
                    speech_detected = True
                    silence_start = None
                    audio_chunks.append(data)
                elif speech_detected:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start >= self.vad_silence_duration:
                        break
        finally:
            stream.stop()
            stream.close()

        if not audio_chunks:
            return ""

        pcm = b"".join(audio_chunks)
        audio = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
        segments, _ = self.model.transcribe(audio)
        return "".join(segment.text for segment in segments).strip()


class PiperTTS(TextToSpeech):
    """Text to speech engine using ``piper-tts`` and ``sounddevice``."""

    def __init__(self, model_path: str) -> None:
        from io import BytesIO
        from piper import PiperVoice

        self.voice = PiperVoice.load(model_path)
        self.sample_rate = self.voice.config.sample_rate
        self._queue: queue.Queue[str] = queue.Queue()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self._buffer_cls = BytesIO

    def _run(self) -> None:
        while True:
            text = self._queue.get()
            if text is None:  # type: ignore[comparison-overlap]
                break
            if not self._stop_event.is_set():
                buf = self._buffer_cls()
                with wave.open(buf, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)  # 2 bytes for 16-bit audio
                    wf.setframerate(self.sample_rate)
                    self.voice.synthesize(text, wf)
                audio = (
                    np.frombuffer(buf.getvalue(), dtype=np.int16).astype(np.float32)
                    / 32768.0
                )
                sd.play(audio, self.sample_rate)
                sd.wait()
            self._queue.task_done()
            self._stop_event.clear()

    def speak(self, tokens: Iterable[str]) -> None:
        self._queue.put("".join(tokens))

    def stop(self) -> None:
        sd.stop()
        self._stop_event.set()
