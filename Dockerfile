# ── Stage 1: Build dependencies ────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /install

COPY requirements.txt .

# Install deps into a prefix we can copy later (keeps final image lean)
RUN pip install --no-cache-dir --prefix=/install/deps -r requirements.txt


# ── Stage 2: Final runtime image ───────────────────────────────────────────────
FROM python:3.12-slim

# Create a non-root user for security
RUN addgroup --system aceest && adduser --system --ingroup aceest aceest

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install/deps /usr/local

# Copy only the application source (not test files or local artifacts)
COPY app.py requirements.txt ./

# Ownership to non-root user
RUN chown -R aceest:aceest /app

USER aceest

EXPOSE 5000

# Gunicorn for production serving; fall back to Flask dev server in CI
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
