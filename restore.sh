#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 1 ]]; then
  echo "Usage: $0 backups/barq_tasks_YYYYmmddTHHMMSSZ.dump" >&2
  exit 2
fi

PROJECT="${PROJECT:-barq-assessment}"
SERVICE="${POSTGRES_SERVICE:-postgres}"
BACKUP_FILE="$1"
TMP="/tmp/barq_restore.dump"

if [[ ! -s "$BACKUP_FILE" ]]; then
  echo "Backup file not found or empty: $BACKUP_FILE" >&2
  exit 2
fi

docker cp "$BACKUP_FILE" "$SERVICE:$TMP"
docker compose -p "$PROJECT" exec -T "$SERVICE" pg_restore \
  -U barq_app \
  -d barq_tasks \
  --clean \
  --if-exists \
  --no-owner \
  "$TMP"
docker compose -p "$PROJECT" exec -T "$SERVICE" rm -f "$TMP"

docker compose -p "$PROJECT" exec -T "$SERVICE" psql \
  -U barq_app \
  -d barq_tasks \
  -c "SELECT count(*) AS restored_records FROM records;"

echo "Restore completed from $BACKUP_FILE"