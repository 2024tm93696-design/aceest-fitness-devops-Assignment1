# ── Stage 1: Build dependencies ────────────────────────────────────────────────
FROM python:3.12.9-slim AS builder

WORKDIR /install

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install/deps -r requirements.txt


# ── Stage 2: Final runtime image ───────────────────────────────────────────────
FROM python:3.12.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN addgroup --system aceest && adduser --system --ingroup aceest aceest

WORKDIR /app

COPY --from=builder /install/deps /usr/local

# Only copy app source — no requirements.txt needed at runtime
COPY app.py ./

RUN chown -R aceest:aceest /app

USER aceest

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]