#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

"$ROOT/scripts/sync-paas-reporting-portal.sh"
paas deploy -m "$ROOT/paas/reporting-portal-admin-mcarroll/tool.yaml" --no-commit --no-repo
