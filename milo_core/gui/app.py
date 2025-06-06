from __future__ import annotations

import random
from typing import Iterable
import threading
from tkinter import Tk, Canvas, Label, Button

from milo_core.memory import ShortTermMemory
from milo_core.llm import LocalModelInterface
from milo_core.memory_manager import MemoryManager
from milo_core.voice.interface import SpeechToText, TextToSpeech


class MiloGUI:
    """Simple Tkinter interface for MILO."""

    def __init__(self, on_end: callable) -> None:
        self.root = Tk()
        self.root.title("MILO")
        self.on_end = on_end

        self.status = Label(self.root, text="Listening", font=("Helvetica", 16))
        self.status.pack(pady=10)

        self.canvas = Canvas(
            self.root, width=200, height=100, bg="black", highlightthickness=0
        )
        self.canvas.pack()

        self.end_button = Button(self.root, text="End Session", command=self._end)
        self.end_button.pack(pady=10)

        self._wave = True
        self.left_eye: int | None = None
        self.right_eye: int | None = None

    def _end(self) -> None:
        self.on_end()
        self.root.quit()

    def start_listening(self) -> None:
        self.status.config(text="Listening")
        self._wave = True
        self.canvas.delete("all")
        self._animate()

    def show_eyes(self) -> None:
        self._wave = False
        self.canvas.delete("all")
        width = 200
        height = 100
        eye_w = 30
        eye_h = 20
        self.left_eye = self.canvas.create_oval(
            width / 2 - 40 - eye_w / 2,
            height / 2 - eye_h / 2,
            width / 2 - 40 + eye_w / 2,
            height / 2 + eye_h / 2,
            fill="#add8e6",
        )
        self.right_eye = self.canvas.create_oval(
            width / 2 + 40 - eye_w / 2,
            height / 2 - eye_h / 2,
            width / 2 + 40 + eye_w / 2,
            height / 2 + eye_h / 2,
            fill="#add8e6",
        )
        self._move_eyes()

    def _move_eyes(self) -> None:
        if self._wave:
            return
        if self.left_eye is None or self.right_eye is None:
            return
        for eye in (self.left_eye, self.right_eye):
            dx = random.randint(-2, 2)
            dy = random.randint(-1, 1)
            self.canvas.move(eye, dx, dy)
        self.root.after(300, self._move_eyes)

    def _animate(self) -> None:
        if not self._wave:
            return
        self.canvas.delete("all")
        width = 200
        height = 100
        bars = 20
        bar_width = width / bars
        for i in range(bars):
            bar_height = random.randint(10, height)
            x0 = i * bar_width
            x1 = x0 + bar_width - 2
            self.canvas.create_rectangle(
                x0, height - bar_height, x1, height, fill="cyan"
            )
        self.root.after(100, self._animate)

    def mainloop(self) -> None:
        self.root.mainloop()


def run_gui(
    model: LocalModelInterface,
    stt: SpeechToText,
    tts: TextToSpeech,
    memory_manager: MemoryManager,
) -> None:
    """Run MILO conversation loop with a GUI."""

    stop_event = threading.Event()
    gui = MiloGUI(stop_event.set)

    def worker() -> None:
        session_memory = ShortTermMemory()
        memory_manager.consolidate_memories()
        while not stop_event.is_set():
            gui.start_listening()
            user_input = stt.listen()
            if stop_event.is_set():
                break
            if not user_input:
                continue
            relevant_memories = memory_manager.retrieve_relevant_memories(user_input)
            if relevant_memories:
                context_str = " ".join(relevant_memories)
                session_memory.add_message(
                    "system", f"Here is some relevant context: {context_str}"
                )
            session_memory.add_message("user", user_input)
            assistant_response_full: list[str] = []

            def generate() -> Iterable[str]:
                history = session_memory.get_messages()
                for token in model.stream_response(history):
                    if stop_event.is_set():
                        break
                    assistant_response_full.append(token)
                    yield token

            def listen_interrupt() -> None:
                stt.listen()
                stop_event.set()
                tts.stop()

            listener = threading.Thread(target=listen_interrupt, daemon=True)
            listener.start()
            gui.show_eyes()
            tts.speak(generate())
            listener.join()

            if stop_event.is_set() and assistant_response_full:
                interrupted = "".join(assistant_response_full)
                session_memory.add_message(
                    "assistant",
                    f"<interrupted_thought>{interrupted}</interrupted_thought>",
                )
            elif assistant_response_full:
                session_memory.add_message(
                    "assistant", "".join(assistant_response_full)
                )

            if user_input.lower() == "goodbye":
                memory_manager.summarize_and_store_session(
                    session_memory.get_messages()
                )
                session_memory.clear()
        gui.root.quit()

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    gui.mainloop()
    stop_event.set()
    thread.join()
