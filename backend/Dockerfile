# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Copy dependency metadata first so dependency installation can be cached
# independently of application source changes.
COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/usr/local/bin:$PATH"

WORKDIR /app

# Create a dedicated non-root runtime user.
RUN groupadd --system loantrack \
    && useradd --system --gid loantrack --create-home loantrack

# Copy only installed runtime dependencies from the builder.
COPY --from=builder /install /usr/local

# Copy application source after dependencies so source changes
# do not invalidate the dependency layer.
COPY app ./app

RUN chown -R loantrack:loantrack /app

USER loantrack

EXPOSE 8000

HEALTHCHECK --interval=30s \
    --timeout=5s \
    --start-period=10s \
    --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3)" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]