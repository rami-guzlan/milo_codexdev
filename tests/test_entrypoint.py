from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_module_entrypoint(tmp_path: Path) -> None:
    stubs = tmp_path / "stubs"
    stubs.mkdir()

    (stubs / "torch.py").write_text("float16 = None")
    transformers = stubs / "transformers"
    transformers.mkdir()
    transformers.joinpath("__init__.py").write_text(
        """
class AutoModelForCausalLM:
    @classmethod
    def from_pretrained(cls, *args, **kwargs):
        return cls()

    def generate(self, *args, **kwargs):
        return [[0]]


class AutoTokenizer:
    @classmethod
    def from_pretrained(cls, *args, **kwargs):
        return cls()

    def __call__(self, *args, **kwargs):
        return type('Obj', (), {'input_ids': [[0]]})

    def decode(self, *args, **kwargs):
        return ''


class TextIteratorStreamer:
    def __iter__(self):
        return iter([])
"""
    )

    # stub whisper and TTS modules so imports succeed
    (stubs / "whisper.py").write_text(
        "def load_model(*args, **kwargs):\n    return None\n"
    )
    tts_pkg = stubs / "TTS"
    tts_pkg.mkdir()
    tts_pkg.joinpath("__init__.py").write_text("")
    api_pkg = tts_pkg / "api"
    api_pkg.mkdir()
    api_pkg.joinpath("__init__.py").write_text(
        "class TTS:\n    def __init__(self, *a, **k):\n        pass\n"
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = f"{stubs}{os.pathsep}{Path.cwd()}"

    result = subprocess.run(
        [sys.executable, "-m", "milo_core", "--help"],
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Run the MILO voice assistant" in result.stdout
