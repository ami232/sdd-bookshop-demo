#!/usr/bin/env bash
# Creates .env on first start. In a Codespace the UI is opened either at the forwarded URL of port 8080
# (browser) or at localhost:8080 (VS Code desktop), so the services must accept both origins (CORS).
# Safe to run again: bash .devcontainer/setup.sh, then docker compose up -d to apply it.
set -euo pipefail
[ -f .env ] || cp .env.example .env
if [ -n "${CODESPACE_NAME:-}" ] && ! grep -q '^UI_ORIGIN=' .env; then
  echo "UI_ORIGIN=http://localhost:8080,https://${CODESPACE_NAME}-8080.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}" >> .env
fi
