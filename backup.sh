#!/usr/bin/env bash
set -euo pipefail
PROJECT="${PROJECT:-barq-assessment}"
SERVICE="${POSTGRES_SERVICE:-postgres}"
BACKUP_DIR="${BACKUP_DIR:-backups}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="${1:-$BACKUP_DIR/barq_tasks_$STAMP.dump}"

mkdir -p "$(dirname "$OUT")"
docker compose -p "$PROJECT" exec -T "$SERVICE" pg_dump \
  -U barq_app \
  -d barq_tasks \
  --format=custom \
  --no-owner \
  --file=- > "$OUT"

echo "Backup written to $OUT"