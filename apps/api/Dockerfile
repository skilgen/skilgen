FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git curl build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml setup.py ./
COPY skilgen/ ./skilgen/
COPY packages/db/ ./packages/db/
COPY packages/__init__.py ./packages/__init__.py
COPY apps/api/requirements.txt ./

RUN pip install --no-cache-dir -e "." && \
    pip install --no-cache-dir -r requirements.txt

COPY apps/api/ ./apps/api/
COPY apps/__init__.py ./apps/__init__.py

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "apps.api.api.index:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
