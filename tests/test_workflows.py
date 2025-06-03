from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from milo_core.workflows import trigger_workflow


WORKFLOW_DIR = Path(".n8n/workflows")


def test_workflow_files_exist_and_are_valid_json() -> None:
    assert WORKFLOW_DIR.exists(), "Workflow directory should exist"

    json_files = list(WORKFLOW_DIR.glob("*.json"))
    assert json_files, "At least one workflow JSON file is required"

    for wf_file in json_files:
        with wf_file.open() as f:
            json.load(f)


@patch("milo_core.workflows.requests.post")
def test_trigger_workflow_sends_post(mock_post) -> None:
    mock_post.return_value.status_code = 200
    response = trigger_workflow("gmail_read", {"foo": "bar"})
    mock_post.assert_called_once_with(
        "http://localhost:5678/webhook/gmail_read", json={"foo": "bar"}
    )
    assert response.status_code == 200
