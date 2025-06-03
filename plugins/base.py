from __future__ import annotations

from abc import ABC, abstractmethod


class BaseSkill(ABC):
    """Base class for all MILO skill plugins."""

    name: str

    @abstractmethod
    def execute(self, *args: object, **kwargs: object) -> object:
        """Run the skill's action."""
        raise NotImplementedError
