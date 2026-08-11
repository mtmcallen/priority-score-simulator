#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

"$ROOT/scripts/sync-paas-reporting-portal-v2.sh"
paas deploy -m "$ROOT/paas/reporting-portal-admin-v2/tool.yaml" --no-commit --no-repo
