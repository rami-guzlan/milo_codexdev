from __future__ import annotations

import importlib
import inspect
import os
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

    def discover_plugins(self, include_tests: bool | None = None) -> None:
        """Find and import skill plugins under ``plugins_path``.

        By default, modules with filenames starting with ``test_`` are skipped.
        Set ``include_tests=True`` or the ``MILO_INCLUDE_TEST_PLUGINS``
        environment variable to load them.
        """
        if not self.plugins_path.exists():
            return

        if include_tests is None:
            include_tests_env = os.getenv("MILO_INCLUDE_TEST_PLUGINS", "").lower()
            include_tests = include_tests_env in {"1", "true", "yes"}

        for module_info in pkgutil.iter_modules([str(self.plugins_path)]):
            if module_info.name.startswith("test_") and not include_tests:
                continue
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
