"""Utilities for interacting with local n8n workflows."""

from __future__ import annotations

from typing import Any, Dict

import requests


DEFAULT_BASE_URL = "http://localhost:5678"


def trigger_workflow(
    workflow_id: str,
    payload: Dict[str, Any] | None = None,
    base_url: str = DEFAULT_BASE_URL,
) -> requests.Response:
    """Trigger an n8n workflow via a local webhook.

    Parameters
    ----------
    workflow_id:
        The unique identifier of the n8n webhook.
    payload:
        Optional JSON payload to send with the webhook POST request.
    base_url:
        Base URL for the locally hosted n8n instance.

    Returns
    -------
    requests.Response
        The response from the webhook request.
    """
    url = f"{base_url}/webhook/{workflow_id}"
    response = requests.post(url, json=payload or {})
    return response
