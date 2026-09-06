#!/usr/bin/env bash
set -euo pipefail
PROJECT="${PROJECT:-barq-assessment}"
SERVICE="${POSTGRES_SERVICE:-postgres}"
BACKUP_DIR="${BACKUP_DIR:-backups}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="${1:-$BACKUP_DIR/barq_tasks_$STAMP.dump}"
TMP="/tmp/barq_tasks_$STAMP.dump"

mkdir -p "$(dirname "$OUT")"
docker compose -p "$PROJECT" exec -T "$SERVICE" pg_dump \
  -U barq_app \
  -d barq_tasks \
  --format=custom \
  --no-owner \
  --file="$TMP"
docker cp "$SERVICE:$TMP" "$OUT"
docker compose -p "$PROJECT" exec -T "$SERVICE" rm -f "$TMP"

if [[ ! -s "$OUT" ]]; then
  echo "Backup failed or empty: $OUT" >&2
  exit 1
fi

echo "Backup written to $OUT"