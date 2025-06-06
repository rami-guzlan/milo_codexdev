from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock, patch

import numpy as np

from milo_core.voice.engines import WhisperSTT, CoquiTTS


def test_whisper_stt_listen() -> None:
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": "hello"}
    with patch("whisper.load_model", return_value=mock_model):
        pcm = np.zeros(16000, dtype=np.float32).tobytes()
        with patch("milo_core.voice.engines.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=pcm)
            stt = WhisperSTT()
            text = stt.listen()
            mock_run.assert_called_once()
            assert text == "hello"


def test_coqui_tts_speak(monkeypatch) -> None:
    # create dummy TTS module
    tts_module = types.ModuleType("TTS")
    api_module = types.ModuleType("TTS.api")
    tts_instance = MagicMock()
    api_module.TTS = MagicMock(return_value=tts_instance)
    tts_module.api = api_module
    sys.modules["TTS"] = tts_module
    sys.modules["TTS.api"] = api_module

    class DummyThread:
        def __init__(self, target, daemon=False):
            self.target = target

        def start(self):
            pass

    with patch("milo_core.voice.engines.threading.Thread", DummyThread):
        with patch("milo_core.voice.engines.subprocess.Popen") as mock_popen:
            proc = MagicMock()
            proc.stdin = MagicMock()
            mock_popen.return_value = proc
            tts_instance.synthesizer.output_sample_rate = 16000
            tts_instance.tts.return_value = np.array([0.0], dtype=np.float32)
            tts = CoquiTTS()
            tts.speak(["hi"])
            tts._queue.put(None)
            tts._run()
            mock_popen.assert_called_once()

    del sys.modules["TTS"]
    del sys.modules["TTS.api"]
