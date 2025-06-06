from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock, patch

import numpy as np

from milo_core.voice.engines import WhisperSTT, PiperTTS


def test_whisper_stt_listen() -> None:
    mock_model = MagicMock()
    mock_model.transcribe.return_value = (
        [type("Seg", (object,), {"text": "hello"})()],
        None,
    )
    with patch("faster_whisper.WhisperModel", return_value=mock_model):
        pcm = np.zeros(16000, dtype=np.float32).tobytes()
        with patch("milo_core.voice.engines.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=pcm)
            stt = WhisperSTT()
            text = stt.listen()
            mock_run.assert_called_once()
            assert text == "hello"


def test_piper_tts_speak(monkeypatch) -> None:
    # create dummy piper module
    piper_module = types.ModuleType("piper")
    voice_module = types.ModuleType("piper.voice")
    voice_instance = MagicMock()
    voice_module.PiperVoice = MagicMock()
    voice_module.PiperVoice.load.return_value = voice_instance
    piper_module.voice = voice_module
    sys.modules["piper"] = piper_module
    sys.modules["piper.voice"] = voice_module

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
            voice_instance.config.sample_rate = 16000
            voice_instance.synthesize_stream_raw.return_value = [b"a"]
            tts = PiperTTS("model", "config")
            tts.speak(["hi"])
            tts._queue.put(None)
            tts._run()
            mock_popen.assert_called_once()

    del sys.modules["piper"]
    del sys.modules["piper.voice"]
