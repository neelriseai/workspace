"""Scaffold module generated from `tests/integration/settings.py`."""

from __future__ import annotations

import json

import os

from dataclasses import dataclass

from pathlib import Path

def _env_bool(name: str, default: bool) -> bool:
    """
    Prompt:
    Implement this function: `_env_bool(name: str, default: bool) -> bool`.
    Keep the same arguments and return contract while recreating behavior.
    """
    raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

@dataclass(frozen=True)
class IntegrationSettings:
    """Prompt scaffold for class `IntegrationSettings` with original members/signatures."""
    base_url: str

    browser_engine: str

    browser_channel: str | None

    headless: bool

    artifacts_root: Path

    reports_dir: Path

    logs_dir: Path

    screenshots_dir: Path

    videos_dir: Path

    metadata_dir: Path

    junit_xml_path: Path

    cucumber_json_path: Path

    step_report_jsonl: Path

    healing_calls_jsonl: Path

    html_report_path: Path

    screenshot_each_test: bool

    screenshot_on_failure: bool

    screenshot_each_step: bool

    video_each_test: bool

    video_width: int

    video_height: int

def load_settings(config_path: Path | None = None) -> IntegrationSettings:
    """
    Prompt:
    Implement this function: `load_settings(config_path: Path | None = None) -> IntegrationSettings`.
    Keep the same arguments and return contract while recreating behavior.
    """
    raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

def ensure_artifact_dirs(settings: IntegrationSettings) -> None:
    """
    Prompt:
    Implement this function: `ensure_artifact_dirs(settings: IntegrationSettings) -> None`.
    Keep the same arguments and return contract while recreating behavior.
    """
    raise NotImplementedError("Scaffold stub: implement based on the prompt above.")
