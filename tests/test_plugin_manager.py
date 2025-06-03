from __future__ import annotations

from milo_core.plugin_manager import PluginManager
from plugins.base import BaseSkill


def test_discover_plugins():
    manager = PluginManager()
    manager.discover_plugins()
    skill = manager.get_skill_by_name("test")
    assert skill is not None
    assert isinstance(skill, BaseSkill)
    assert skill.execute() == "executed"


def test_local_model_interface_stub():
    from milo_core.llm.interface import StubLocalModel, LocalModelInterface

    model: LocalModelInterface = StubLocalModel()
    for method in (
        model.load_model,
        lambda: model.generate_response("hi"),
        model.unload,
    ):
        try:
            method()
        except NotImplementedError:
            pass
        else:
            raise AssertionError("Stub methods should raise NotImplementedError")
