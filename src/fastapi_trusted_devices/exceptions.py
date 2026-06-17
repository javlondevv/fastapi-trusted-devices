"""Typed exceptions with stable, machine-readable error codes.

Every error carries a stable string ``code`` so API clients can branch on it
without parsing human-readable messages. :func:`install_exception_handlers`
wires these into a FastAPI app so they render as consistent JSON.
"""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class TrustedDeviceError(Exception):
    """Base class for all trusted-device errors.

    Attributes:
        code: Stable, machine-readable identifier (never localised).
        status_code: HTTP status used by the default exception handler.
        detail: Human-readable description.
    """

    code: str = "trusted_device_error"
    status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.__class__.__doc__ or self.code
        super().__init__(self.detail)


class DeviceUIDMissing(TrustedDeviceError):
    """No device identifier was supplied with the request."""

    code = "device_uid_missing"
    status_code = status.HTTP_401_UNAUTHORIZED


class DeviceNotRecognized(TrustedDeviceError):
    """The device is not registered for this user."""

    code = "device_not_recognized"
    status_code = status.HTTP_401_UNAUTHORIZED


class DeviceLacksEditPermission(TrustedDeviceError):
    """This device may not modify other devices."""

    code = "device_lacks_edit_permission"
    status_code = status.HTTP_403_FORBIDDEN


class DeviceLacksDeletePermission(TrustedDeviceError):
    """This device may not revoke other devices."""

    code = "device_lacks_delete_permission"
    status_code = status.HTTP_403_FORBIDDEN


class DeviceEditingDisabled(TrustedDeviceError):
    """The device is too recent to be edited (update delay not elapsed)."""

    code = "device_editing_disabled"
    status_code = status.HTTP_409_CONFLICT


class DeviceDeletionDisabled(TrustedDeviceError):
    """The device is too recent to be revoked (delete delay not elapsed)."""

    code = "device_deletion_disabled"
    status_code = status.HTTP_409_CONFLICT


def install_exception_handlers(app: FastAPI) -> None:
    """Register a JSON handler for :class:`TrustedDeviceError` on ``app``."""

    async def _handler(_: Request, exc: Exception) -> JSONResponse:
        assert isinstance(exc, TrustedDeviceError)  # registered for this type
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "detail": exc.detail}},
        )

    app.add_exception_handler(TrustedDeviceError, _handler)
