# Installation

## Requirements

- Python **3.10+**
- FastAPI **≥ 0.110**
- SQLAlchemy **≥ 2.0** (async) — only if you use the bundled repository
- Pydantic **≥ 2.5**

## Install

```bash
pip install fastapi-trusted-devices
```

## Optional extras

```bash
# httpx-based geolocation backend (roadmap 0.2+)
pip install "fastapi-trusted-devices[geo]"

# PyJWT token helpers (roadmap 0.3+)
pip install "fastapi-trusted-devices[jwt]"
```

!!! note
    The `geo` and `jwt` extras are declared today but their helper modules land
    in upcoming releases (see the [Roadmap](roadmap.md)). Installing them now
    simply pre-pulls `httpx` / `pyjwt`.

## Async driver

The bundled `SQLAlchemyDeviceRepository` needs an async driver for your database.
For SQLite (great for trying it out):

```bash
pip install aiosqlite
```

For PostgreSQL:

```bash
pip install "asyncpg"
```

## Verify

```bash
python -c "import fastapi_trusted_devices as t; print('ok')"
```
