from __future__ import annotations

from googlesearch import search

from plugins.base import BaseSkill


class GoogleSearchSkill(BaseSkill):
    """Skill to perform a web search using the googlesearch library."""

    name = "googlesearch"

    def execute(self, query: str, num_results: int = 5) -> str:  # type: ignore[override]
        """Return the top URLs for ``query``."""
        results: list[str] = []
        for url in search(query, num_results=num_results):
            results.append(url)
        return "\n".join(results)
