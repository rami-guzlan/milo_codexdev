from __future__ import annotations

from unittest.mock import MagicMock, patch

from milo_core import commands
from milo_core.main import main


class DummySkill:
    name = "test"

    def execute(self) -> str:
        return "executed"


def test_end_to_end_skill_execution() -> None:
    skill = DummySkill()
    plugin_manager = MagicMock()
    plugin_manager.get_skill_by_name.return_value = skill

    stt = MagicMock()
    stt.listen.return_value = "Milo, run the test skill"

    model = MagicMock()
    model.stream_response.return_value = iter(['{"type": "skill", "name": "test"}'])

    tts = MagicMock()

    memory_manager = MagicMock()

    def fake_converse(model_arg, stt_arg, tts_arg, mem_arg):
        stt_arg.listen()
        tokens = list(model_arg.stream_response([]))
        command_dict = eval(tokens[0])
        result = commands.execute_command(command_dict, plugin_manager)
        tts_arg.speak([result])

    with (
        patch("milo_core.main.GemmaLocalModel", return_value=model),
        patch("milo_core.main.WhisperSTT", return_value=stt),
        patch("milo_core.main.CoquiTTS", return_value=tts),
        patch("milo_core.main.PluginManager", return_value=plugin_manager),
        patch("milo_core.memory_manager.MemoryManager", return_value=memory_manager),
        patch("milo_core.main.converse", side_effect=fake_converse),
        patch(
            "milo_core.commands.execute_command", wraps=commands.execute_command
        ) as exec_mock,
    ):
        main(["--no-gui"])
        exec_mock.assert_called_once_with(
            {"type": "skill", "name": "test"}, plugin_manager
        )

    plugin_manager.get_skill_by_name.assert_called_with("test")
    tts.speak.assert_called_with(["executed"])
