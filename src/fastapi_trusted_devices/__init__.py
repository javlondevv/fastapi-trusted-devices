"""fastapi-trusted-devices: async trusted-device management for FastAPI."""

from __future__ import annotations

from .config import TrustedDeviceConfig
from .events import EventHooks
from .exceptions import (
    DeviceDeletionDisabled,
    DeviceEditingDisabled,
    DeviceLacksDeletePermission,
    DeviceLacksEditPermission,
    DeviceNotRecognized,
    DeviceUIDMissing,
    TrustedDeviceError,
    install_exception_handlers,
)
from .facade import TrustedDevices
from .models import Base, Device
from .repository import DeviceRepository, SQLAlchemyDeviceRepository
from .schemas import DeviceOut, DeviceUpdate
from .service import TrustedDeviceService

__all__ = [
    "Base",
    "Device",
    "DeviceDeletionDisabled",
    "DeviceEditingDisabled",
    "DeviceLacksDeletePermission",
    "DeviceLacksEditPermission",
    "DeviceNotRecognized",
    "DeviceOut",
    "DeviceRepository",
    "DeviceUIDMissing",
    "DeviceUpdate",
    "EventHooks",
    "SQLAlchemyDeviceRepository",
    "TrustedDeviceConfig",
    "TrustedDeviceError",
    "TrustedDeviceService",
    "TrustedDevices",
    "install_exception_handlers",
]

__version__ = "0.1.0"
