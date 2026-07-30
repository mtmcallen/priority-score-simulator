#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_DIR="$ROOT/paas/reporting-portal-admin-mcarroll"
DEPLOY_DIR="$APP_DIR/deploy"

rm -rf "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"
cp "$ROOT/docs/designs/reporting-portal-admin-prototype.html" "$DEPLOY_DIR/index.html"

echo "Prepared reporting-portal-admin-mcarroll ($(du -sh "$DEPLOY_DIR" | cut -f1))"
