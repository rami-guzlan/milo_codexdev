from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock, patch

import numpy as np

from milo_core.voice.engines import WhisperSTT, CoquiTTS


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
    mock_model.transcribe.assert_called_once()


def test_coqui_tts_speak(monkeypatch) -> None:
    # create dummy Coqui TTS module
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
            tts_instance.synthesizer.output_sample_rate = 22050
            tts_instance.tts.return_value = np.array([0.1, -0.1], dtype=np.float32)
            tts = CoquiTTS("model", "config")
            tts.speak(["hi"])
            tts._queue.put(None)
            tts._run()
            mock_popen.assert_called_once()
            tts_instance.tts.assert_called_with("hi")
            proc.stdin.write.assert_called()

    del sys.modules["TTS"]
    del sys.modules["TTS.api"]
