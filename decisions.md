# Technical Decisions

## 1. NGINX as the only published service
- Choice: Publish only NGINX on loopback `127.0.0.1:${PUBLIC_PORT:-8080}`.
- Why: The assessment requires a single public entrypoint while app, PostgreSQL, and Redis remain private.
- Alternative: Publish each service for debugging.
- Trade-off: Debugging internal services requires `docker compose exec`, but the attack surface is smaller.
- Evidence: `docker-compose.yml`, `python validate.py --project barq-assessment --wait 120`.
- Production improvement: Add TLS termination and a managed ingress/load balancer.

## 2. Separate frontend and backend networks
- Choice: Put NGINX only on `frontend`; apps on `frontend` and `backend`; PostgreSQL and Redis only on internal `backend`.
- Why: This blocks direct NGINX-to-database/cache network access and keeps dependencies isolated.
- Alternative: One flat Compose network.
- Trade-off: More explicit network configuration, but clearer boundaries.
- Evidence: `validate.py` network isolation checks.
- Production improvement: Use network policies/security groups.

## 3. Real readiness checks, light liveness checks
- Choice: `/health` checks process responsiveness only; `/ready` checks PostgreSQL and Redis.
- Why: This preserves the app contract and avoids treating dependency failure as process death.
- Alternative: Make `/health` check dependencies too.
- Trade-off: Operators must understand the difference between alive and ready.
- Evidence: `tests/test_app.py` and `validate.py`.
- Production improvement: Export separate metrics for dependency latency and failure counts.

## 4. Named volumes for persistence
- Choice: Use `postgres-data` for PostgreSQL and `redis-data` with Redis AOF enabled.
- Why: Records and Redis state survive container recreation and normal `docker compose down`.
- Alternative: Container-local storage or tmpfs.
- Trade-off: Cleanup requires intentional volume removal.
- Evidence: `docker-compose.yml`, backup/restore scripts.
- Production improvement: Use managed PostgreSQL/Redis with automated backups.

## 5. Non-root Flask container
- Choice: Create UID/GID 10001 and run the app as `app`.
- Why: Avoid root/privileged operation where practical.
- Alternative: Run as root for simpler file permissions.
- Trade-off: Files must be copied with correct ownership.
- Evidence: `Dockerfile`.
- Production improvement: Use gunicorn with tuned workers and read-only filesystem constraints.

## 6. Bounded validation and failure tests
- Choice: Validation uses finite waits and non-zero failure exits; failure test restores the stopped backend in cleanup.
- Why: CI and video evidence need deterministic pass/fail behavior.
- Alternative: Manual curl-only verification.
- Trade-off: Scripts are stricter and may fail if the machine is very slow.
- Evidence: `validate.py`, `failure_test.py`.
- Production improvement: Add smoke tests in deployment pipelines and continuous synthetic checks.