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
    def from_pretrained(cls, *a, **k):
        return cls()
    def generate(self, *a, **k):
        return [[0]]


class AutoTokenizer:
    @classmethod
    def from_pretrained(cls, *a, **k):
        return cls()
    def __call__(self, *a, **k):
        return type('Obj', (), {'input_ids': [[0]]})
    def decode(self, *a, **k):
        return ''


class TextIteratorStreamer:
    def __iter__(self):
        return iter([])
"""
    )

    # stub audio and tts modules so imports succeed
    (stubs / "sounddevice.py").write_text(
        "class RawInputStream:\n"
        "    def __init__(self,*a,**k): pass\n"
        "    def start(self): pass\n"
        "    def read(self,n): return (b'', False)\n"
        "    def stop(self): pass\n"
        "    def close(self): pass\n"
        "\n"
        "def play(*a, **k): pass\n"
        "def wait(*a, **k): pass\n"
        "def stop(*a, **k): pass\n"
    )
    piper_pkg = stubs / "piper"
    piper_pkg.mkdir()
    piper_pkg.joinpath("__init__.py").write_text(
        "class PiperVoice:\n    @staticmethod\n    def load(*a, **k):\n        return type('V', (), {'config': type('C', (), {'sample_rate': 16000})(), 'synthesize': lambda self, t, w: None})()\n"
    )

    st = stubs / "sentence_transformers"
    st.mkdir()
    st.joinpath("__init__.py").write_text(
        "class SentenceTransformer:\n    def __init__(self, *a, **k): pass\n    def encode(self, t): return [0.1]\n"
    )

    milo_stub = stubs / "milo_core"
    milo_stub.mkdir()
    milo_stub.joinpath("__init__.py").write_text("")
    milo_stub.joinpath("memory_manager.py").write_text(
        "class MemoryManager:\n    def __init__(self, *a, **k): pass\n    def consolidate_memories(self): pass\n"
    )
    gui_dir = milo_stub / "gui"
    gui_dir.mkdir()
    gui_dir.joinpath("__init__.py").write_text("def run_gui(*a, **k):\n    pass\n")
    llm_dir = milo_stub / "llm"
    llm_dir.mkdir()
    llm_dir.joinpath("__init__.py").write_text("")
    llm_dir.joinpath("huggingface.py").write_text(
        "class HuggingFaceModel:\n    def __init__(self, *a, **k): pass\n    def load_model(self): pass\n    def unload(self): pass\n    def stream_response(self, *a, **k): return iter([])\n    def generate_response(self, prompt): return ''\n"
    )
    milo_stub.joinpath("__main__.py").write_text(
        "def main():\n    pass\n\nif __name__ == '__main__':\n    main()\n"
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = f"{stubs}{os.pathsep}{Path.cwd()}"

    result = subprocess.run(
        [sys.executable, "-m", "milo_core"],
        env=env,
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
