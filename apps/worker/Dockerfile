FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml setup.py ./
COPY skilgen/ ./skilgen/
COPY packages/db/ ./packages/db/
COPY packages/__init__.py ./packages/__init__.py
COPY apps/worker/requirements.txt ./

RUN pip install --no-cache-dir -e "." && \
    pip install --no-cache-dir -r requirements.txt

COPY apps/api/ ./apps/api/
COPY apps/worker/ ./apps/worker/
COPY apps/__init__.py ./apps/__init__.py

CMD ["celery", "-A", "apps.worker.worker.celery_app", "worker", "--loglevel=info", "--concurrency=2"]
