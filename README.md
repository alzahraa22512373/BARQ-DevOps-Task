<img src="assets/barq-logo.svg" alt="BARQ Systems" width="180">

# BARQ DevOps Assessment

Repaired Docker Compose environment for the BARQ Flask API. The public entrypoint is NGINX on `127.0.0.1:${PUBLIC_PORT:-8080}`. Flask runs in two private app containers, PostgreSQL stores `/records`, and Redis stores `/counter`.

## Quick Start

```bash
cp .env.example .env
docker compose -p barq-assessment up --build -d
docker compose -p barq-assessment ps -a
python validate.py --project barq-assessment --wait 120
```

## Useful Checks

```bash
curl -i http://127.0.0.1:8080/
curl -i http://127.0.0.1:8080/health
curl -i http://127.0.0.1:8080/ready
curl -i http://127.0.0.1:8080/instance
curl -i -H 'Content-Type: application/json' -d '{"title":"Persistence proof"}' http://127.0.0.1:8080/records
curl -i http://127.0.0.1:8080/records
curl -i http://127.0.0.1:8080/counter
```

To prove both backends through NGINX:

```bash
for i in $(seq 1 20); do curl -s http://127.0.0.1:8080/instance; echo; done
```

## Tests

```bash
python -m unittest discover -s tests -v
docker compose -p barq-assessment config --quiet
python validate.py --project barq-assessment --wait 120
python failure_test.py --project barq-assessment --url http://127.0.0.1:8080
```

`validate.py` checks public readiness, all required endpoints, both backend identities, Docker health, network isolation, and that only NGINX publishes a host port.

## Backup and Restore

```bash
./backup.sh
./restore.sh backups/<backup-file>.dump
```

PowerShell fallback on Windows if Bash cannot access Docker Desktop:

```powershell
docker compose -p barq-assessment exec -T postgres pg_dump -U barq_app -d barq_tasks --format=custom --no-owner --file=/tmp/backup.dump
docker cp postgres:/tmp/backup.dump backups\backup.dump
docker cp backups\backup.dump postgres:/tmp/restore.dump
docker compose -p barq-assessment exec -T postgres pg_restore -U barq_app -d barq_tasks --clean --if-exists --no-owner /tmp/restore.dump
```

Persistence proof without deleting volumes:

```bash
curl -H 'Content-Type: application/json' -d '{"title":"Restart proof"}' http://127.0.0.1:8080/records
docker compose -p barq-assessment restart app-01 app-02 postgres
python validate.py --project barq-assessment --wait 120
curl http://127.0.0.1:8080/records
```

## Stop and Cleanup

Preserve data:

```bash
docker compose -p barq-assessment down
```

Remove lab data only after backup/evidence is complete:

```bash
docker compose -p barq-assessment down --volumes
```

## Video Runbook

Before recording, start from a clean commit and stopped environment. During the video, run the commands above, then run `./video_challenge.sh` once. Diagnose the injected fault without `docker compose down`, repair it, change `PUBLIC_PORT` to `8090`, add `app-03`, prove all three instances respond, rerun validation, then commit and push on screen.

## Evidence Files

- `architecture.png`
- `EVIDENCE_INDEX.md`
- `log_analysis.md`
- `troubleshooting.md`
- `decisions.md`
- `security_review.md`
- `AI_USAGE.md`