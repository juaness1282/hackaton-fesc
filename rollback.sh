#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ "${1:-}" != affiliations ]; then
  echo "Uso: ./rollback.sh affiliations" >&2
  exit 2
fi
docker compose run --rm --no-deps gateway python migration.py LEGACY
echo "Afiliaciones en LEGACY; Subsidios conserva el camino original."
