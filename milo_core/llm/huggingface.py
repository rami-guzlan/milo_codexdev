from __future__ import annotations

from threading import Thread
from typing import Iterator, List

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextIteratorStreamer,
)

from milo_core.memory import Message
from .interface import LocalModelInterface


class HuggingFaceModel(LocalModelInterface):
    """Load and interact with a Hugging Face transformer model."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16,
        )

    def load_model(self) -> None:
        return None

    def unload(self) -> None:
        return None

    def generate_response(self, prompt: str, max_new_tokens: int = 256) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        output = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
        return self.tokenizer.decode(output[0], skip_special_tokens=True)

    def stream_response(
        self, history: List[Message], max_new_tokens: int = 256
    ) -> Iterator[str]:
        messages = [{"role": m.role, "content": m.content} for m in history]
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True)
        thread = Thread(
            target=self.model.generate,
            kwargs={"streamer": streamer, "max_new_tokens": max_new_tokens, **inputs},
        )
        thread.start()
        for token in streamer:
            yield token
        thread.join()
