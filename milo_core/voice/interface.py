from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable


class SpeechToText(ABC):
    """Abstract speech-to-text engine."""

    @abstractmethod
    def listen(self) -> str:
        """Listen for a single utterance and return transcribed text."""
        raise NotImplementedError


class TextToSpeech(ABC):
    """Abstract text-to-speech engine."""

    @abstractmethod
    def speak(self, tokens: Iterable[str]) -> None:
        """Speak an iterable of text chunks."""
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        """Immediately stop speaking."""
        raise NotImplementedError
