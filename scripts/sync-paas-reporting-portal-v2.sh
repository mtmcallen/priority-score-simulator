#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_DIR="$ROOT/paas/reporting-portal-admin-v2"
DEPLOY_DIR="$APP_DIR/deploy"

rm -rf "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"
cp "$ROOT/docs/designs/reporting-portal-admin-prototype-v2.html" "$DEPLOY_DIR/index.html"

echo "Prepared reporting-portal-admin-v2 ($(du -sh "$DEPLOY_DIR" | cut -f1))"
