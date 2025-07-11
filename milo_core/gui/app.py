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
    """Basic Tkinter-based chat window."""

    def __init__(self, on_end: Callable[[], None]) -> None:
        self.root = Tk()
        self.root.title("MILO Chat")
        self.on_end = on_end

        self.root.protocol("WM_DELETE_WINDOW", self._end)

        frame = Frame(self.root)
        frame.pack(fill="both", expand=True)

        self.text_area = Text(frame, state="disabled", wrap="word")
        self.text_area.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(frame, command=self.text_area.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_area.configure(yscrollcommand=scrollbar.set)

        self.text_area.tag_configure("user", foreground="blue")
        self.text_area.tag_configure("assistant", foreground="green")

        entry_frame = Frame(self.root)
        entry_frame.pack(fill="x")

        self.entry = Entry(entry_frame)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self._handle_send)

        send_btn = Button(entry_frame, text="Send", command=self._handle_send)
        send_btn.pack(side="right")

        self._send_callback: Callable[[str], None] | None = None
        self._stream_tag: str | None = None

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
        """Insert a completed message into the chat display."""

        tag = "user" if author == "You" else "assistant"
        self.text_area.configure(state="normal")
        self.text_area.insert(END, f"{author}: {message}\n", tag)
        self.text_area.configure(state="disabled")
        self.text_area.see(END)

    def start_stream_message(self, author: str) -> None:
        """Prepare to stream a new message from ``author``."""

        tag = "user" if author == "You" else "assistant"
        self._stream_tag = tag
        self.text_area.configure(state="normal")
        self.text_area.insert(END, f"{author}: ", tag)
        self.text_area.configure(state="disabled")
        self.text_area.see(END)

    def append_stream_token(self, token: str) -> None:
        """Append a streamed token to the current message."""

        if self._stream_tag is None:
            return
        self.text_area.configure(state="normal")
        self.text_area.insert(END, token, self._stream_tag)
        self.text_area.configure(state="disabled")
        self.text_area.see(END)

    def end_stream_message(self) -> None:
        """Finalize a streaming message."""

        if self._stream_tag is None:
            return
        self.text_area.configure(state="normal")
        self.text_area.insert(END, "\n")
        self.text_area.configure(state="disabled")
        self._stream_tag = None
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
        gui.start_stream_message("M.I.L.O")
        tokens: list[str] = []
        for token in model.stream_response(history):
            tokens.append(token)
            gui.append_stream_token(token)
        gui.end_stream_message()
        full_msg = "".join(tokens)
        session_memory.add_message("assistant", full_msg)
        if user_input.lower() == "goodbye":
            memory_manager.summarize_and_store_session(session_memory.get_messages())
            session_memory.clear()

    gui.set_send_callback(process_input)
    gui.mainloop()
