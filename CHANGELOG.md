# Changelog

All notable changes to this project are documented here. This project adheres to
[Semantic Versioning](https://semver.org) (from `1.0.0` onward) and the
[Keep a Changelog](https://keepachangelog.com) format.

## [Unreleased]

## [0.1.0] - 2026-06-18

### Added
- Initial release: trusted-device registry for FastAPI.
- `Device` SQLAlchemy 2.0 (async) model and declarative `Base`.
- `DeviceRepository` protocol with a SQLAlchemy adapter.
- `TrustedDeviceService` core logic (register, list, update, revoke,
  permission checks).
- `TrustedDevices` facade: mountable `APIRouter` and FastAPI dependencies
  (`require_trusted_device`, `current_device`).
- Endpoints: list, update, delete, logout, revoke-all.
- Typed exception hierarchy with stable error codes and installable
  exception handlers.
- Async event hooks (`on_device_created`, `on_device_revoked`).
- `py.typed` marker; `mypy --strict` clean.

[Unreleased]: https://github.com/javlondevv/fastapi-trusted-devices/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/javlondevv/fastapi-trusted-devices/releases/tag/v0.1.0
