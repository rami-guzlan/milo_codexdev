from __future__ import annotations

import importlib
import inspect
import pkgutil
from pathlib import Path
from types import ModuleType
from typing import List

from plugins.base import BaseSkill


class PluginManager:
    """Discover and load skill plugins from the ``/plugins`` directory."""

    def __init__(self, plugins_path: Path | None = None) -> None:
        self.plugins_path = (
            plugins_path or Path(__file__).resolve().parent.parent / "plugins"
        )
        self.skills: List[BaseSkill] = []

    def discover_plugins(self) -> None:
        """Find and import skill plugins under ``plugins_path``."""
        if not self.plugins_path.exists():
            return

        for module_info in pkgutil.iter_modules([str(self.plugins_path)]):
            module = importlib.import_module(f"plugins.{module_info.name}")
            self._load_from_module(module)

    def _load_from_module(self, module: ModuleType) -> None:
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if obj is BaseSkill or not issubclass(obj, BaseSkill):
                continue
            self.skills.append(obj())

    def get_skill_by_name(self, name: str) -> BaseSkill | None:
        """Retrieve a skill instance by its ``name`` attribute."""
        for skill in self.skills:
            if skill.name == name:
                return skill
        return None
