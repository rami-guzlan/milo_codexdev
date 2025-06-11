from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np

from milo_core.voice.engines import Pyttsx3TTS, WhisperSTT


def test_whisper_stt_listen_with_vad() -> None:
    mock_model = MagicMock()
    mock_model.transcribe.return_value = (
        [type("Seg", (object,), {"text": "hello"})()],
        None,
    )

    speech_chunk = (np.ones(480, dtype=np.int16) * 1000).tobytes()
    silence_chunk = np.zeros(480, dtype=np.int16).tobytes()

    stream = MagicMock()
    stream.read.side_effect = [speech_chunk, speech_chunk, silence_chunk, silence_chunk]

    pa_instance = MagicMock()
    pa_instance.open.return_value = stream

    vad_instance = MagicMock()
    vad_instance.is_speech.side_effect = [True, True, False, False]

    time_values = [0.0, 1.1, 1.2]

    with (
        patch("faster_whisper.WhisperModel", return_value=mock_model),
        patch("milo_core.voice.engines.pyaudio.PyAudio", return_value=pa_instance),
        patch("milo_core.voice.engines.webrtcvad.Vad", return_value=vad_instance),
        patch("milo_core.voice.engines.time.time", side_effect=time_values),
    ):
        stt = WhisperSTT()
        text = stt.listen()

    assert text == "hello"
    concatenated = (
        np.frombuffer(speech_chunk + speech_chunk, dtype=np.int16).astype(np.float32)
        / 32768.0
    )
    np.testing.assert_array_equal(
        mock_model.transcribe.call_args[0][0],
        concatenated,
    )
    mock_model.transcribe.assert_called_once()


def test_pyttsx3_tts_speak(monkeypatch) -> None:
    engine = MagicMock()

    class DummyThread:
        def __init__(self, target, daemon=False):
            self.target = target

        def start(self):
            pass

    monkeypatch.setattr("pyttsx3.init", lambda: engine)

    with patch("milo_core.voice.engines.threading.Thread", DummyThread):
        tts = Pyttsx3TTS()
        tts.speak(["hi"])
        tts._queue.put(None)
        tts._run()
        engine.say.assert_called_with("hi")
        engine.runAndWait.assert_called()
