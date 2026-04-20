"""Shared message types for the observability module."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any


@dataclass
class Registration:
    agent_id: str
    agent_name: str
    fqdn: str
    cpu: str
    gpu: str
    os: str
    arch: str
    python_version: str
    geolocation: dict[str, Any]


@dataclass
class Log:
    agent_id: str
    agent_name: str
    message: str
    level: str = 'INFO'


@dataclass
class Stats:
    agent_id: str
    cpu_percent: float
    memory_rss_mb: float
    memory_vms_mb: float
    gpu: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class UserPrompt:
    agent_id: str
    prompt: str
    responses: list[str]


Message = Registration | Log | Stats | UserPrompt
