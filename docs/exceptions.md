# Exceptions

All errors raised by the library inherit from `TrustedDeviceError`. Each carries
a stable string `code` and an HTTP `status_code`, so clients can branch on the
code without parsing prose.

```python
class TrustedDeviceError(Exception):
    code: str = "trusted_device_error"
    status_code: int = 400  # HTTP_400_BAD_REQUEST

    def __init__(self, detail: str | None = None) -> None: ...
```

## Hierarchy

| Exception | `code` | HTTP status | Meaning |
|---|---|---|---|
| `TrustedDeviceError` | `trusted_device_error` | 400 | Base class for all errors below. |
| `DeviceUIDMissing` | `device_uid_missing` | 401 | No device identifier supplied with the request. |
| `DeviceNotRecognized` | `device_not_recognized` | 401 | The device is not registered for this user. |
| `DeviceLacksEditPermission` | `device_lacks_edit_permission` | 403 | This device may not modify other devices. |
| `DeviceLacksDeletePermission` | `device_lacks_delete_permission` | 403 | This device may not revoke other devices. |
| `DeviceEditingDisabled` | `device_editing_disabled` | 409 | Device too recent to edit (update delay not elapsed). |
| `DeviceDeletionDisabled` | `device_deletion_disabled` | 409 | Device too recent to revoke (delete delay not elapsed). |

## Installing the handlers

Call once at startup so these surface as clean JSON instead of 500s:

```python
td.install_exception_handlers(app)
# or the standalone function:
from fastapi_trusted_devices import install_exception_handlers
install_exception_handlers(app)
```

## Response format

Handled errors render as:

```json
{
  "error": {
    "code": "device_not_recognized",
    "detail": "The device is not registered for this user."
  }
}
```

The HTTP status code matches the table above (e.g. `401` for
`device_not_recognized`).

## Catching them in code

```python
from fastapi_trusted_devices import TrustedDeviceError, DeviceNotRecognized

try:
    device = await service.get_recognized(user_id, device_uid)
except DeviceNotRecognized:
    ...  # handle unknown device
except TrustedDeviceError as exc:
    ...  # any other library error; exc.code / exc.status_code available
```
