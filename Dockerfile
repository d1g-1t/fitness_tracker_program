FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock* ./
RUN uv pip install --system --no-cache-dir \
    "fastapi>=0.104.1" \
    "uvicorn[standard]>=0.24.0" \
    "sqlalchemy>=2.0.23" \
    "alembic>=1.12.1" \
    "asyncpg>=0.29.0" \
    "redis>=5.0.1" \
    "pydantic>=2.5.0" \
    "pydantic-settings>=2.1.0" \
    "email-validator>=2.1.0" \
    "python-jose[cryptography]>=3.3.0" \
    "passlib[bcrypt]>=1.7.4" \
    "python-multipart>=0.0.6" \
    "python-dateutil>=2.8.2"

COPY . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
