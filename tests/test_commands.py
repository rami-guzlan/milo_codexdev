from __future__ import annotations

from unittest.mock import MagicMock, patch

from milo_core.commands import execute_command, CommandError
from milo_core.plugin_manager import PluginManager
from plugins.test_skill import TestSkill


def setup_manager() -> PluginManager:
    pm = PluginManager()
    # manually register the test skill instead of discovery to avoid filesystem dependency
    pm.skills = [TestSkill()]
    return pm


def test_execute_skill_success() -> None:
    pm = setup_manager()
    result = execute_command({"type": "skill", "name": "test"}, pm)
    assert result == "executed"


def test_execute_skill_unknown() -> None:
    pm = setup_manager()
    try:
        execute_command({"type": "skill", "name": "unknown"}, pm)
    except CommandError as exc:
        assert "Unknown skill" in str(exc)
    else:  # pragma: no cover - ensure failure if not raised
        raise AssertionError("Expected CommandError")


@patch("milo_core.commands.trigger_workflow")
def test_execute_workflow_success(mock_trigger) -> None:
    mock_resp = MagicMock()
    mock_resp.ok = True
    mock_trigger.return_value = mock_resp
    pm = setup_manager()
    result = execute_command({"type": "workflow", "id": "wf"}, pm)
    assert result is mock_resp
    mock_trigger.assert_called_once_with("wf", None)


@patch("milo_core.commands.trigger_workflow")
def test_execute_workflow_failure(mock_trigger) -> None:
    mock_resp = MagicMock()
    mock_resp.ok = False
    mock_resp.status_code = 500
    mock_trigger.return_value = mock_resp
    pm = setup_manager()
    try:
        execute_command({"type": "workflow", "id": "wf"}, pm)
    except CommandError as exc:
        assert "failed" in str(exc)
    else:
        raise AssertionError("Expected CommandError")
