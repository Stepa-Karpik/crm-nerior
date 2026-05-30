#!/usr/bin/env bash
set -euo pipefail
APP_DIR=${APP_DIR:-/opt/nerior/crm}
REPO_URL=${REPO_URL:-https://github.com/Stepa-Karpik/crm-nerior.git}
mkdir -p /opt/nerior
if [ ! -d "$APP_DIR/.git" ]; then
  rm -rf "$APP_DIR"
  git clone "$REPO_URL" "$APP_DIR"
fi
cd "$APP_DIR"
git fetch origin main
git reset --hard origin/main
if [ ! -f .env ]; then cp .env.example .env; fi
docker network inspect nerior_shared >/dev/null 2>&1 || docker network create nerior_shared
docker compose --project-name nerior_crm up -d --build --remove-orphans
docker image prune -f
