# Discoverability setup — fastapi-trusted-devices

Run once, before launching. Requires the `gh` CLI authenticated as `javlondevv`
(`gh auth login`). Commands target `javlondevv/fastapi-trusted-devices`.

## 1. Topics

Topics are how people browse GitHub. Add all of them:

```bash
gh repo edit javlondevv/fastapi-trusted-devices \
  --add-topic fastapi \
  --add-topic security \
  --add-topic authentication \
  --add-topic sessions \
  --add-topic device-management \
  --add-topic jwt \
  --add-topic python \
  --add-topic asgi \
  --add-topic session-security
```

## 2. About sidebar (description + homepage)

```bash
gh repo edit javlondevv/fastapi-trusted-devices \
  --description "Trusted-device management and session security for FastAPI — bind sessions to a device, list & revoke devices, detect suspicious activity. Auth-agnostic, async SQLAlchemy." \
  --homepage "https://pypi.org/project/fastapi-trusted-devices/"
```

## 3. Enable Discussions

```bash
gh repo edit javlondevv/fastapi-trusted-devices --enable-discussions
```

## 4. Labels

`good first issue` and `help wanted` are special: GitHub surfaces them on the
[contribute](https://github.com/contribute) page and in the sidebar. Create the
set (ignore errors for labels that already exist):

```bash
gh label create "good first issue" -c "#7057ff" -d "Good for newcomers"            -R javlondevv/fastapi-trusted-devices
gh label create "help wanted"      -c "#008672" -d "Extra attention is welcome"    -R javlondevv/fastapi-trusted-devices
gh label create "enhancement"      -c "#a2eeef" -d "New feature or request"        -R javlondevv/fastapi-trusted-devices
gh label create "discussion"       -c "#d4c5f9" -d "Needs design discussion"       -R javlondevv/fastapi-trusted-devices
```

## 5. Starter issues

Concrete, scoped, newcomer-friendly tasks. An empty issue tracker reads as
"abandoned"; a few `good first issue`s read as "active and welcoming."

```bash
gh issue create -R javlondevv/fastapi-trusted-devices \
  --label "good first issue" \
  --title "Add an example app using the [jwt] extra" \
  --body $'The README quickstart wires up the device flow but doesn'\''t show the PyJWT helpers from the `[jwt]` extra.\n\n**Task:** add `examples/jwt_app.py` that issues a signed token carrying the `device_uid`, then uses `get_device_uid` to read it back from the request. Keep it runnable (`uvicorn examples.jwt_app:app`).\n\n**Pointers:** see the existing quickstart in the README and the `[jwt]` extra in `pyproject.toml`. Ask in the issue if anything is unclear — happy to guide.'

gh issue create -R javlondevv/fastapi-trusted-devices \
  --label "good first issue" \
  --title "Docs: implement a custom in-memory DeviceRepository" \
  --body $'`DeviceRepository` is a Protocol so storage is pluggable, but there'\''s no minimal example of writing your own backend.\n\n**Task:** add a short docs section (and a small `examples/in_memory_repo.py`) implementing the `DeviceRepository` protocol with a plain dict — useful for tests and for understanding the contract.\n\nGreat first issue to learn the core interfaces. Comment to claim it.'

gh issue create -R javlondevv/fastapi-trusted-devices \
  --label "help wanted" \
  --title "Tests: cover revoke-all edge cases" \
  --body $'We want more coverage around `POST /revoke-all`:\n\n- revoking when the user has exactly one device (the current one)\n- ensuring the current device is preserved\n- behaviour when `device_uid` is missing/unknown\n- idempotency on a second call\n\n**Task:** add `pytest`/`pytest-asyncio` tests for these. See `CONTRIBUTING.md` for the dev setup (`pip install -e ".[dev]"`, `pytest -q`).'

gh issue create -R javlondevv/fastapi-trusted-devices \
  --label "enhancement" --label "help wanted" \
  --title "0.2: geolocation backend stub (httpx) behind the [geo] extra" \
  --body $'Toward the 0.2 roadmap item. Define the geolocation backend interface and ship an httpx-based stub behind the `[geo]` extra that maps an IP -> coarse location, with caching and a no-op default.\n\n**Scope for this issue:** the interface + a stub implementation + tests; suspicious-login *detection* that consumes it can be a follow-up. Let'\''s discuss the interface in the issue before coding.'
```

## 6. Awesome-list submissions

Durable, compounding traffic. Fork each list, add one line, open a PR.

- **awesome-fastapi** (e.g. [`mrahmadt/awesome-fastapi`](https://github.com/mrahmadt/awesome-fastapi)
  and other `awesome-fastapi` lists) — under an Auth/Security section:

  ```markdown
  - [fastapi-trusted-devices](https://github.com/javlondevv/fastapi-trusted-devices) - Trusted-device management and session security: bind sessions to a device, list/revoke devices, per-device permissions. Auth-agnostic, async SQLAlchemy.
  ```

- **awesome-python** ([`vinta/awesome-python`](https://github.com/vinta/awesome-python))
  — under *Authentication* / security:

  ```markdown
  - [fastapi-trusted-devices](https://github.com/javlondevv/fastapi-trusted-devices) - Trusted-device and session-security layer for FastAPI apps.
  ```

PR tips: follow each list's CONTRIBUTING (alphabetical order, exact bullet
format, one entry per PR), and keep the description factual — maintainers reject
hype.
