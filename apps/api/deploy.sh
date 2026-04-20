#!/usr/bin/env bash
set -euo pipefail

echo "================================================================"
echo "  [FAKE DEPLOY] apps/api"
echo "================================================================"
echo "Would deploy FastAPI app to target environment."
echo "App: api"
echo "Commit: ${GITHUB_SHA:-local}"
echo "Ref:    ${GITHUB_REF:-local}"
echo "Time:   $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
echo "================================================================"
