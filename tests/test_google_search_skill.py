from __future__ import annotations

from unittest.mock import patch

from plugins.google_search_skill import GoogleSearchSkill
from milo_core.commands import execute_command
from milo_core.plugin_manager import PluginManager


@patch("plugins.google_search_skill.search")
def test_google_search_skill_execute(mock_search) -> None:
    mock_search.return_value = ["http://example.com", "http://example.org"]
    skill = GoogleSearchSkill()
    result = skill.execute("test", num_results=2)
    assert result == "http://example.com\nhttp://example.org"


@patch("plugins.google_search_skill.search")
def test_execute_command_with_google_search(mock_search) -> None:
    mock_search.return_value = ["http://foo.com"]
    pm = PluginManager()
    pm.skills = [GoogleSearchSkill()]
    result = execute_command(
        {"type": "skill", "name": "googlesearch", "args": ["query"]}, pm
    )
    assert result == "http://foo.com"
