#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEPLOY="$ROOT/deploy"

FLYERS=(
  staff-ssr-hype-flyer.html
  ambient-listening-hype-flyer.html
  patient-prioritization-hype-flyer.html
)

rm -rf "$DEPLOY"
mkdir -p "$DEPLOY/assets" "$DEPLOY/docs"

cp "$ROOT/index.html" "$DEPLOY/"
cp "$ROOT/assets/cipherhealth-logo-mark.svg" "$DEPLOY/assets/"
cp "$ROOT/assets/cipherhealth-logo.svg" "$DEPLOY/assets/"

for flyer in "${FLYERS[@]}"; do
  cp "$ROOT/docs/$flyer" "$DEPLOY/docs/"
done

cat > "$DEPLOY/docs/index.html" <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CipherHealth Hype Flyers</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; max-width: 40rem; margin: 2rem auto; padding: 0 1rem; color: #2d2660; }
    h1 { font-size: 1.35rem; }
    ul { line-height: 1.8; padding-left: 1.25rem; }
    a { color: #00b4a4; }
  </style>
</head>
<body>
  <h1>Customer-facing hype flyers</h1>
  <p>Open a flyer, customize highlighted fields, paste a QR code, then print or save as PDF.</p>
  <ul>
    <li><a href="staff-ssr-hype-flyer.html">Staff Self-Service Rounding (Staff SSR)</a></li>
    <li><a href="ambient-listening-hype-flyer.html">Ambient Listening</a></li>
    <li><a href="patient-prioritization-hype-flyer.html">Patient Prioritization</a></li>
  </ul>
  <p><a href="../">← Patient Prioritization Simulator</a></p>
</body>
</html>
EOF

echo "Prepared PaaS deploy bundle at deploy/ ($(du -sh "$DEPLOY" | cut -f1))"
echo "  Flyers: ${FLYERS[*]}"
