#!/bin/bash
set -e

echo "Installing Skillayer..."

command -v docker >/dev/null 2>&1 || {
  echo "Docker is required"
  exit 1
}
command -v git >/dev/null 2>&1 || {
  echo "Git is required"
  exit 1
}
command -v docker-compose >/dev/null 2>&1 || docker compose version >/dev/null 2>&1 || {
  echo "Docker Compose is required"
  exit 1
}

INSTALL_ROOT=/opt/skillayer
REPO_URL=https://github.com/RaviChanduUmmadisetti/skilgen.git
REPO_DIR="${INSTALL_ROOT}/repo"

mkdir -p "${INSTALL_ROOT}"

if [ ! -d "${REPO_DIR}/.git" ]; then
  git clone --depth 1 "${REPO_URL}" "${REPO_DIR}"
fi

cd "${REPO_DIR}"

read -p "Dashboard URL [http://localhost:3000]: " NEXT_PUBLIC_DASHBOARD_URL
NEXT_PUBLIC_DASHBOARD_URL=${NEXT_PUBLIC_DASHBOARD_URL:-http://localhost:3000}

read -p "API URL [http://localhost:8000]: " NEXT_PUBLIC_API_URL
NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-http://localhost:8000}

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
NEXT_PUBLIC_DASHBOARD_URL=${NEXT_PUBLIC_DASHBOARD_URL}
NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
API_URL=${NEXT_PUBLIC_API_URL}
GITHUB_APP_ID=${GITHUB_APP_ID}
GITHUB_WEBHOOK_SECRET=${GITHUB_WEBHOOK_SECRET}
WORKOS_API_KEY=${WORKOS_API_KEY}
WORKOS_CLIENT_ID=${WORKOS_CLIENT_ID}
WORKOS_REDIRECT_URI=${NEXT_PUBLIC_DASHBOARD_URL}/callback
NEXT_PUBLIC_WORKOS_REDIRECT_URI=${NEXT_PUBLIC_DASHBOARD_URL}/callback
WORKOS_COOKIE_PASSWORD=${COOKIE_PASSWORD}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
EOF

docker compose -f infra/docker/docker-compose.prod.yml up -d --build

echo ""
echo "Skillayer is running!"
echo "Dashboard: http://localhost:3000"
echo "API:       http://localhost:8000"
