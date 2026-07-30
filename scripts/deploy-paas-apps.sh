#!/usr/bin/env bash
# Sync local sources and deploy all Cipher PaaS apps in this repo.
#
# Each app is identified by the stable `name:` in its tool.yaml — redeploys update
# the same live URL; they do not create a new app. Use --commit --save --repo so
# deploy source is also committed to the org paas_apps monorepo for persistence.
#
# Usage:
#   ./scripts/deploy-paas-apps.sh              # sync + deploy everything
#   ./scripts/deploy-paas-apps.sh pp-device-requirements-mcarroll al-device-requirements-mcarroll
#   PAAS_REPO=SolarCS/paas_apps ./scripts/deploy-paas-apps.sh
#
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PAAS_REPO="${PAAS_REPO:-SolarCS/paas_apps}"
DEPLOY_FLAGS=(--commit --save --repo "$PAAS_REPO")

# manifest paths in deploy order (simulator → flyers → device reqs → other)
ALL_MANIFESTS=(
  "$ROOT/tool.yaml"
  "$ROOT/paas/staff-ssr-hype-flyer-mcarroll/tool.yaml"
  "$ROOT/paas/ambient-listening-hype-flyer-mcarroll/tool.yaml"
  "$ROOT/paas/al-device-requirements-mcarroll/tool.yaml"
  "$ROOT/paas/al-device-requirements-ios-mcarroll/tool.yaml"
  "$ROOT/paas/al-device-requirements-android-mcarroll/tool.yaml"
  "$ROOT/paas/patient-prioritization-flyer-mcarroll/tool.yaml"
  "$ROOT/paas/pp-device-requirements-mcarroll/tool.yaml"
  "$ROOT/paas/pp-device-requirements-ios-mcarroll/tool.yaml"
  "$ROOT/paas/pp-device-requirements-android-mcarroll/tool.yaml"
  "$ROOT/paas/home-final-walkthrough-mcarroll/tool.yaml"
  "$ROOT/paas/reporting-portal-admin-mcarroll/tool.yaml"
  "$ROOT/paas/change-log-voting-mcarroll/tool.yaml"
)

sync_all() {
  echo "Syncing deploy bundles …"
  "$ROOT/scripts/sync-paas-deploy.sh"
  "$ROOT/scripts/sync-paas-flyer-apps.sh"
  "$ROOT/scripts/sync-paas-walkthrough.sh"
  "$ROOT/scripts/sync-paas-change-log-voting.sh"
  "$ROOT/scripts/sync-paas-reporting-portal.sh"
}

deploy_manifest() {
  local manifest="$1"
  local app_dir app_name

  if [[ ! -f "$manifest" ]]; then
    echo "ERROR: missing manifest: $manifest" >&2
    exit 1
  fi

  app_dir="$(dirname "$manifest")"
  app_name="$(basename "$app_dir")"
  if [[ "$app_dir" == "$ROOT" ]]; then
    app_name="priority-score-sim-mcarroll"
  fi

  echo
  echo "==> Deploying $app_name"
  echo "    manifest: ${manifest#$ROOT/}"
  paas deploy -m "$manifest" "${DEPLOY_FLAGS[@]}"
}

manifest_for_filter() {
  local filter="$1" manifest app_name app_dir
  for manifest in "${ALL_MANIFESTS[@]}"; do
    app_dir="$(dirname "$manifest")"
    app_name="$(basename "$app_dir")"
    if [[ "$manifest" == "$ROOT/tool.yaml" ]]; then
      app_name="priority-score-sim-mcarroll"
    fi
    if [[ "$app_name" == "$filter" ]]; then
      echo "$manifest"
      return 0
    fi
  done
  echo "ERROR: unknown app '$filter'. Known apps:" >&2
  for manifest in "${ALL_MANIFESTS[@]}"; do
    app_name="$(basename "$(dirname "$manifest")")"
    [[ "$manifest" == "$ROOT/tool.yaml" ]] && app_name="priority-score-sim-mcarroll"
    echo "  - $app_name" >&2
  done
  exit 1
}

main() {
  sync_all

  if (($# > 0)); then
    for filter in "$@"; do
      deploy_manifest "$(manifest_for_filter "$filter")"
    done
  else
    for manifest in "${ALL_MANIFESTS[@]}"; do
      deploy_manifest "$manifest"
    done
  fi

  echo
  echo "Done. Apps update in place at their existing *.tools.cipherhealth.dev URLs."
  echo "Source committed to $PAAS_REPO (per-app subfolder) with --commit --save."
}

main "$@"
