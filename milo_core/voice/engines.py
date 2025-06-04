from __future__ import annotations

import queue
import threading
from typing import Iterable

import pyttsx3
import speech_recognition as sr

from .interface import SpeechToText, TextToSpeech


class PocketsphinxSTT(SpeechToText):
    """Speech recognition using the built-in PocketSphinx engine."""

    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def listen(self) -> str:
        with self.microphone as source:
            audio = self.recognizer.listen(source)
        try:
            return self.recognizer.recognize_sphinx(audio)
        except sr.UnknownValueError:
            return ""


class Pyttsx3TTS(TextToSpeech):
    """Simple TTS engine using ``pyttsx3``."""

    def __init__(self) -> None:
        self.engine = pyttsx3.init()
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
                self.engine.say(text)
                self.engine.runAndWait()
            self._queue.task_done()
            self._stop_event.clear()

    def speak(self, tokens: Iterable[str]) -> None:
        for token in tokens:
            if self._stop_event.is_set():
                break
            self._queue.put(token)

    def stop(self) -> None:
        self._stop_event.set()
        self.engine.stop()
