#!/bin/bash
set -e

echo "Installing Skillayer..."

command -v docker >/dev/null 2>&1 || {
  echo "Docker is required"
  exit 1
}
command -v docker-compose >/dev/null 2>&1 || docker compose version >/dev/null 2>&1 || {
  echo "Docker Compose is required"
  exit 1
}

mkdir -p /opt/skillayer
cd /opt/skillayer

curl -sSL https://raw.githubusercontent.com/RaviChanduUmmadisetti/skilgen/main/infra/docker/docker-compose.prod.yml -o docker-compose.yml

read -p "GitHub App ID: " GITHUB_APP_ID
read -p "GitHub Webhook Secret: " GITHUB_WEBHOOK_SECRET
read -p "WorkOS API Key: " WORKOS_API_KEY
read -p "WorkOS Client ID: " WORKOS_CLIENT_ID

POSTGRES_PASSWORD=$(openssl rand -hex 32)
COOKIE_PASSWORD=$(openssl rand -hex 32)

cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://skillayer:${POSTGRES_PASSWORD}@postgres:5432/skillayer
REDIS_URL=redis://redis:6379/0
DEPLOYMENT_MODE=selfhosted
GITHUB_APP_ID=${GITHUB_APP_ID}
GITHUB_WEBHOOK_SECRET=${GITHUB_WEBHOOK_SECRET}
WORKOS_API_KEY=${WORKOS_API_KEY}
WORKOS_CLIENT_ID=${WORKOS_CLIENT_ID}
WORKOS_COOKIE_PASSWORD=${COOKIE_PASSWORD}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
EOF

docker compose up -d

echo ""
echo "Skillayer is running!"
echo "Dashboard: http://localhost:3000"
echo "API:       http://localhost:8000"
