#!/usr/bin/env bash
# Creates .env on first start. In a Codespace the UI's address is the forwarded URL of port 8080.
set -euo pipefail
[ -f .env ] || cp .env.example .env
if [ -n "${CODESPACE_NAME:-}" ] && ! grep -q '^UI_ORIGIN=' .env; then
  echo "UI_ORIGIN=https://${CODESPACE_NAME}-8080.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}" >> .env
fi
