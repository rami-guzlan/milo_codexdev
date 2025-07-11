from __future__ import annotations


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


    def __init__(self, on_end: Callable[[], None]) -> None:
        self.root = Tk()
        self.root.title("MILO Chat")
        self.on_end = on_end



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

    gui.set_send_callback(process_input)
    gui.mainloop()
