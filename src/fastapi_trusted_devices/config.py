"""Configuration for the trusted-devices layer."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TrustedDeviceConfig(BaseModel):
    """Tunable behaviour for the trusted-devices layer."""

    model_config = {"frozen": True, "extra": "forbid"}

    # Max concurrent devices per user; None disables the cap. When exceeded,
    # the oldest device is evicted on registration.
    max_devices_per_user: int | None = Field(default=None, ge=1)
    # Minimum device age (minutes) before it may be renamed.
    update_delay_minutes: int = Field(default=0, ge=0)
    # Minimum device age (minutes) before its owner may revoke it.
    delete_delay_minutes: int = Field(default=0, ge=0)
    # Trusted-proxy depth for X-Forwarded-For parsing.
    trusted_proxy_depth: int = Field(default=0, ge=0)
    # Window (seconds) used by concurrent-session detection.
    concurrent_session_window_seconds: int = Field(default=60, ge=0)
