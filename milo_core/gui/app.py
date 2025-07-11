from __future__ import annotations

from typing import Callable
from tkinter import (
    Tk,
    Text,
    Entry,
    Button,
    Scrollbar,
    Frame,
    END,
)

from milo_core.llm import LocalModelInterface
from milo_core.memory import ShortTermMemory
from milo_core.memory_manager import MemoryManager
from milo_core.voice.interface import SpeechToText, TextToSpeech


class MiloGUI:
    """Simple text-based chat interface for MILO."""

    def __init__(self, on_end: Callable[[], None]) -> None:
        self.root = Tk()
        self.root.title("MILO")
        self.on_end = on_end

        self.text_area = Text(self.root, state="disabled", wrap="word")
        self.scrollbar = Scrollbar(self.root, command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=self.scrollbar.set)
        self.text_area.pack(side="top", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        bottom = Frame(self.root)
        bottom.pack(side="bottom", fill="x")

        self.entry = Entry(bottom)
        self.entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.entry.bind("<Return>", self._handle_send)

        self.send_button = Button(bottom, text="Send", command=self._handle_send)
        self.send_button.pack(side="right", padx=5, pady=5)

        self.end_button = Button(bottom, text="End Session", command=self._end)
        self.end_button.pack(side="right", padx=5, pady=5)

        self._send_callback: Callable[[str], None] | None = None

    def set_send_callback(self, callback: Callable[[str], None]) -> None:
        """Register the function to call when the user sends a message."""

        self._send_callback = callback

    def _handle_send(self, event: object | None = None) -> None:
        if not self._send_callback:
            return
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, END)
        self._send_callback(text)

    def add_message(self, author: str, message: str) -> None:
        """Display a message in the chat history."""

        self.text_area.configure(state="normal")
        self.text_area.insert(END, f"{author}: {message}\n")
        self.text_area.configure(state="disabled")
        self.text_area.see(END)

    def _end(self) -> None:
        self.on_end()
        self.root.quit()

    def mainloop(self) -> None:
        self.entry.focus()
        self.root.mainloop()


def run_gui(
    model: LocalModelInterface,
    stt: SpeechToText,
    tts: TextToSpeech,
    memory_manager: MemoryManager,
) -> None:
    """Run MILO conversation loop with a text-based GUI."""

    session_memory = ShortTermMemory()
    memory_manager.consolidate_memories()

    gui = MiloGUI(lambda: None)

    def process_input(user_input: str) -> None:
        gui.add_message("You", user_input)
        relevant_memories = memory_manager.retrieve_relevant_memories(user_input)
        if relevant_memories:
            context_str = " ".join(relevant_memories)
            session_memory.add_message(
                "system", f"Here is some relevant context: {context_str}"
            )
        session_memory.add_message("user", user_input)
        history = session_memory.get_messages()
        assistant_tokens = model.stream_response(history)
        assistant_response = "".join(assistant_tokens)
        session_memory.add_message("assistant", assistant_response)
        gui.add_message("M.I.L.O", assistant_response)
        if user_input.lower() == "goodbye":
            memory_manager.summarize_and_store_session(session_memory.get_messages())
            session_memory.clear()

    gui.set_send_callback(process_input)
    gui.mainloop()
