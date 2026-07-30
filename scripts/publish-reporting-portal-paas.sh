#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

"$ROOT/scripts/sync-paas-reporting-portal.sh"
exec "$ROOT/scripts/deploy-paas-apps.sh" reporting-portal-admin-mcarroll
