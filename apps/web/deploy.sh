#!/usr/bin/env bash
set -euo pipefail

echo "================================================================"
echo "  [FAKE DEPLOY] apps/web"
echo "================================================================"
echo "Would deploy Next.js app to target environment."
echo "App: web"
echo "Commit: ${GITHUB_SHA:-local}"
echo "Ref:    ${GITHUB_REF:-local}"
echo "Time:   $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
echo "================================================================"
