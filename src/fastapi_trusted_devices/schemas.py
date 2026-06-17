"""Pydantic v2 request/response schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DeviceOut(BaseModel):
    """Public representation of a device."""

    model_config = ConfigDict(from_attributes=True)

    device_uid: uuid.UUID
    name: str | None = None
    user_agent: str | None = None
    ip_address: str | None = None
    last_ip: str | None = None
    country: str | None = None
    region: str | None = None
    city: str | None = None
    created_at: datetime
    last_seen: datetime
    can_update_other_devices: bool
    can_delete_other_devices: bool
    #: True when this row is the device that issued the current request.
    is_current: bool = False


class DeviceUpdate(BaseModel):
    """Mutable fields a caller may change on a device."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, max_length=255)
    can_update_other_devices: bool | None = None
    can_delete_other_devices: bool | None = None
