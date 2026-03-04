"""Scaffold module generated from `tests/integration/settings.py`."""

from __future__ import annotations

import json

import os

from dataclasses import dataclass

from pathlib import Path

def _env_bool(name: str, default: bool) -> bool:
    # Prompt: Implement this function keeping the same signature and return contract.
    # Signature: _env_bool(name: str, default: bool) -> bool
    # Dependent call placeholders from original flow:
    # - os.getenv(name)
    # - value.strip().casefold()
    # - value.strip()
    # TODO: Replace placeholder with a concrete `bool` value.
    return None

@dataclass(frozen=True)
class IntegrationSettings:
    """Prompt scaffold class preserving original members/signatures."""
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
    # Prompt: Implement this function keeping the same signature and return contract.
    # Signature: load_settings(config_path: Path | None = None) -> IntegrationSettings
    # Dependent call placeholders from original flow:
    # - Path(__file__).with_name('config.json')
    # - config_path.open('r', encoding='utf-8')
    # - json.load(fh)
    # - os.getenv('XH_BASE_URL', str(raw.get('base_url') or '')).rstrip('/')
    # - os.getenv('XH_BASE_URL', str(raw.get('base_url') or ''))
    # - raw.get('base_url')
    # TODO: Replace placeholder with a concrete `IntegrationSettings` value.
    return None

def ensure_artifact_dirs(settings: IntegrationSettings) -> None:
    # Prompt: Implement this function keeping the same signature and return contract.
    # Signature: ensure_artifact_dirs(settings: IntegrationSettings) -> None
    # Dependent call placeholders from original flow:
    # - settings.artifacts_root.mkdir(parents=True, exist_ok=True)
    # - settings.reports_dir.mkdir(parents=True, exist_ok=True)
    # - settings.logs_dir.mkdir(parents=True, exist_ok=True)
    # - settings.screenshots_dir.mkdir(parents=True, exist_ok=True)
    # - settings.videos_dir.mkdir(parents=True, exist_ok=True)
    # - settings.metadata_dir.mkdir(parents=True, exist_ok=True)
    return None
