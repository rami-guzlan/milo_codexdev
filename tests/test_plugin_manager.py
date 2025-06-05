from __future__ import annotations

from milo_core.plugin_manager import PluginManager
from plugins.base import BaseSkill


def test_discover_plugins_ignores_test_plugins_by_default() -> None:
    manager = PluginManager()
    manager.discover_plugins()
    assert manager.get_skill_by_name("test") is None


def test_discover_plugins_can_include_tests(monkeypatch) -> None:
    monkeypatch.setenv("MILO_INCLUDE_TEST_PLUGINS", "1")
    manager = PluginManager()
    manager.discover_plugins()
    skill = manager.get_skill_by_name("test")
    assert isinstance(skill, BaseSkill)
    assert skill.execute() == "executed"


def test_local_model_interface_stub():
    from milo_core.llm.interface import StubLocalModel, LocalModelInterface

    model: LocalModelInterface = StubLocalModel()
    for method in (
        model.load_model,
        lambda: model.generate_response("hi"),
        lambda: next(model.stream_response("hi")),
        model.unload,
    ):
        try:
            method()
        except NotImplementedError:
            pass
        else:
            raise AssertionError("Stub methods should raise NotImplementedError")
