from __future__ import annotations

import threading
from pathlib import Path
from typing import Iterator

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextIteratorStreamer,
)

from .interface import LocalModelInterface


class GemmaLocalModel(LocalModelInterface):
    """Load and interact with a local Gemma model."""

    def __init__(self, model_dir: str | Path) -> None:
        self.model_dir = Path(model_dir)
        self.model = None
        self.tokenizer = None

    def load_model(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_dir, torch_dtype=torch.float16
        )
        self.model.to("cpu")

    def generate_response(self, prompt: str, max_new_tokens: int = 256) -> str:
        assert self.model is not None and self.tokenizer is not None, "Model not loaded"
        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids
        output_ids = self.model.generate(input_ids, max_new_tokens=max_new_tokens)
        return self.tokenizer.decode(output_ids[0], skip_special_tokens=True)

    def stream_response(self, prompt: str, max_new_tokens: int = 256) -> Iterator[str]:
        assert self.model is not None and self.tokenizer is not None, "Model not loaded"
        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids
        streamer = TextIteratorStreamer(
            self.tokenizer, skip_prompt=True, skip_special_tokens=True
        )
        thread = threading.Thread(
            target=self.model.generate,
            kwargs={
                "input_ids": input_ids,
                "max_new_tokens": max_new_tokens,
                "streamer": streamer,
            },
        )
        thread.start()
        for token in streamer:
            yield token
        thread.join()

    def unload(self) -> None:
        self.model = None
        self.tokenizer = None
