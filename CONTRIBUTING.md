# Contributing

Thanks for your interest in `fastapi-trusted-devices`.

## Development setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Checks (must pass before a PR is merged — CI enforces these)

```bash
ruff check .          # lint + import order
mypy                  # strict type checking of the package
pytest -q             # async test suite
```

## Conventions

- Public API changes must update `CHANGELOG.md` under `[Unreleased]`.
- New behaviour ships with tests (service-level and/or API-level).
- Keep the core (`service.py`) framework-free; HTTP concerns live in
  `router.py` / `facade.py`; storage lives behind `DeviceRepository`.
- The library targets Python 3.10+ and must stay `mypy --strict` clean.

## Releases

Maintainers tag `vX.Y.Z`; the release workflow builds and publishes to PyPI via
Trusted Publishing (OIDC). Bump `version` in `pyproject.toml` and
`__version__`, move the `[Unreleased]` changelog entries under the new version,
then push the tag.
