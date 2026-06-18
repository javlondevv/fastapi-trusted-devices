# Contributing

Thanks for your interest in `fastapi-trusted-devices`! Bug reports, feature
ideas, and PRs are all welcome.

## Development setup

```bash
git clone https://github.com/javlondevv/fastapi-trusted-devices.git
cd fastapi-trusted-devices
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Checks (CI enforces these)

```bash
ruff check .      # lint + import order
mypy              # strict type checking
pytest -q         # async test suite
```

## Conventions

- Public API changes must update `CHANGELOG.md` under `[Unreleased]`.
- New behaviour ships with tests (service-level and/or API-level).
- Keep the core (`service.py`) framework-free; HTTP concerns live in
  `router.py` / `facade.py`; storage lives behind `DeviceRepository`.
- Targets Python 3.10+ and must stay `mypy --strict` clean.

## Good first issues

Check the
[**good first issue**](https://github.com/javlondevv/fastapi-trusted-devices/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
and
[**help wanted**](https://github.com/javlondevv/fastapi-trusted-devices/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
labels for friendly entry points. Please also read the
[Code of Conduct](https://github.com/javlondevv/fastapi-trusted-devices/blob/main/CODE_OF_CONDUCT.md).

## Releases

Maintainers tag `vX.Y.Z`; the release workflow builds and publishes to PyPI via
Trusted Publishing (OIDC). Bump `version` in `pyproject.toml` and `__version__`,
move `[Unreleased]` changelog entries under the new version, then push the tag.
