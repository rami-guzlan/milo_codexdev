from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock, patch

import numpy as np

from milo_core.voice.engines import WhisperSTT, PiperTTS


def test_whisper_stt_listen_with_vad() -> None:
    mock_model = MagicMock()
    mock_model.transcribe.return_value = (
        [type("Seg", (object,), {"text": "hello"})()],
        None,
    )

    speech_chunk = np.ones(16000, dtype=np.float32).tobytes()
    silence_chunk = np.zeros(16000, dtype=np.float32).tobytes()

    stream = MagicMock()
    stream.read.side_effect = [speech_chunk, speech_chunk, silence_chunk, silence_chunk]

    pa_instance = MagicMock()
    pa_instance.open.return_value = stream

    vad_model = MagicMock()
    vad_model.side_effect = [
        MagicMock(item=MagicMock(return_value=0.6)),
        MagicMock(item=MagicMock(return_value=0.6)),
        MagicMock(item=MagicMock(return_value=0.0)),
        MagicMock(item=MagicMock(return_value=0.0)),
    ]

    time_values = [0.0, 1.1, 1.2]

    with (
        patch("faster_whisper.WhisperModel", return_value=mock_model),
        patch("milo_core.voice.engines.pyaudio.PyAudio", return_value=pa_instance),
        patch(
            "milo_core.voice.engines.torch.hub.load",
            return_value=(vad_model, (None, None, None, None, None)),
        ),
        patch("milo_core.voice.engines.time.time", side_effect=time_values),
    ):
        stt = WhisperSTT()
        text = stt.listen()

    assert text == "hello"
    concatenated = np.concatenate([np.frombuffer(speech_chunk, dtype=np.float32)] * 2)
    np.testing.assert_array_equal(
        mock_model.transcribe.call_args[0][0],
        concatenated,
    )


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
