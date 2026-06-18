# Roadmap

`fastapi-trusted-devices` is `0.1.0` — **alpha**. The core device registry and
management endpoints are usable today; later milestones layer on geolocation and
threat detection.

| Milestone | Scope |
|---|---|
| **0.1** ✅ | Core registry, CRUD endpoints, dependencies, SQLAlchemy adapter, event hooks, typed exceptions. |
| **0.2** | Geolocation backend + cache, `X-Forwarded-For` parsing, suspicious-login detection. |
| **0.3** | Concurrent-session / hijack detection, max-device eviction policies, rate limiting, PyJWT helpers, this docs site. |
| **1.0** | API freeze + semver guarantee. |

## Optional extras (declared now, filled in later)

### `[geo]`

```bash
pip install "fastapi-trusted-devices[geo]"   # pulls httpx>=0.27
```

Pre-pulls `httpx` for the upcoming geolocation backend, which will populate the
`Device.country` / `region` / `city` fields from the request IP, with a caching
layer. **Helper modules land in 0.2** — installing the extra today simply
ensures the dependency is present.

### `[jwt]`

```bash
pip install "fastapi-trusted-devices[jwt]"   # pulls pyjwt>=2.8
```

Pre-pulls `PyJWT` for the planned token helpers (embedding / validating
`device_uid` inside JWTs). **Helper modules land in 0.3.**

!!! note
    Because the API may change before `1.0`, pin a version (`fastapi-trusted-devices==0.1.*`)
    and watch the [CHANGELOG](https://github.com/javlondevv/fastapi-trusted-devices/blob/main/CHANGELOG.md).

Have a feature in mind? Open an issue or join the
[discussions](https://github.com/javlondevv/fastapi-trusted-devices/discussions).
