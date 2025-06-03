from __future__ import annotations

from plugins.base import BaseSkill


class TestSkill(BaseSkill):
    name = "test"

    def execute(self, *args: object, **kwargs: object) -> str:  # type: ignore[override]
        return "executed"
