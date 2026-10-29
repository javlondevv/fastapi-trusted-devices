# Runnable demo of fastapi-trusted-devices: serves examples/minimal_app.py.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install the library from source, plus the example's runtime needs
# (aiosqlite for the SQLite database, uvicorn to serve it).
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install . "aiosqlite>=0.19" "uvicorn>=0.29" \
    && rm -rf src pyproject.toml README.md LICENSE

COPY examples ./examples

# Non-root user; it owns /app so the example can create ./devices.db there.
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin app \
    && chown app:app /app
USER app

EXPOSE 8000
CMD ["uvicorn", "examples.minimal_app:app", "--host", "0.0.0.0", "--port", "8000"]
