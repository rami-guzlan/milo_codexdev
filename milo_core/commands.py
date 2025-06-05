from __future__ import annotations

import json
from typing import Any, Dict

from .plugin_manager import PluginManager
from .workflows import trigger_workflow


class CommandError(Exception):
    """Raised when a command cannot be parsed or executed."""


def execute_command(
    command: str | Dict[str, Any], plugin_manager: PluginManager
) -> Any:
    """Parse and execute a skill or workflow command.

    Parameters
    ----------
    command:
        JSON string or dictionary describing the action to perform. Expected
        keys:
        ``type`` (``"skill"`` or ``"workflow"``), along with ``name`` for skills
        or ``id`` for workflows. ``args`` and ``kwargs`` are optional for skills,
        ``payload`` is optional for workflows.
    plugin_manager:
        Manager used to look up loaded skills.

    Returns
    -------
    Any
        The result of ``skill.execute`` or the ``requests.Response`` from
        ``trigger_workflow``.
    """

    if isinstance(command, str):
        try:
            data: Dict[str, Any] = json.loads(command)
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive
            raise CommandError("Invalid command JSON") from exc
    else:
        data = command

    cmd_type = data.get("type")
    if cmd_type == "skill":
        skill_name = data.get("name")
        if not skill_name:
            raise CommandError("Missing skill name")
        skill = plugin_manager.get_skill_by_name(str(skill_name))
        if skill is None:
            raise CommandError(f"Unknown skill: {skill_name}")
        args = data.get("args", [])
        kwargs = data.get("kwargs", {})
        return skill.execute(*args, **kwargs)

    if cmd_type == "workflow":
        workflow_id = data.get("id")
        if not workflow_id:
            raise CommandError("Missing workflow id")
        payload = data.get("payload")
        response = trigger_workflow(str(workflow_id), payload)
        if not getattr(response, "ok", False):
            raise CommandError(
                f"Workflow {workflow_id} failed with status {getattr(response, 'status_code', 'unknown')}"
            )
        return response

    raise CommandError("Unsupported command type")
