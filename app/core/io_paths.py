"""Filesystem path helpers for call recordings and transcripts."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


def build_transcript_directory(
    base_dir: Path,
    company: str,
    last_first: str,
    start_time: datetime,
    tz: str,
    status: str,
) -> Path:
    """Return the directory path for storing call artifacts.

    Parameters
    ----------
    base_dir:
        Base directory where transcripts are stored, typically the user's
        ``Documents/Call Transcripts`` folder.
    company:
        Company name associated with the lead.
    last_first:
        Lead's name in ``LastFirst`` format.
    start_time:
        Call start time.
    tz:
        Timezone abbreviation.
    status:
        Disposition of the call.

    Returns
    -------
    Path
        Directory path following the convention described in the project
        specification.
    """
    return (
        base_dir
        / f"{start_time:%Y}"
        / f"{start_time:%m}"
        / f"{company}_{last_first}_{start_time:%Y-%m-%d}_{start_time:%H%M}_{tz}_{status}"
    )
