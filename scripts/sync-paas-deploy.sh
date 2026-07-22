#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEPLOY="$ROOT/deploy"

rm -rf "$DEPLOY"
mkdir -p "$DEPLOY/assets"

cp "$ROOT/index.html" "$DEPLOY/"
cp "$ROOT/assets/cipherhealth-logo-mark.svg" "$DEPLOY/assets/"
cp "$ROOT/assets/cipherhealth-logo.svg" "$DEPLOY/assets/"

echo "Prepared PaaS deploy bundle at deploy/ ($(du -sh "$DEPLOY" | cut -f1))"
