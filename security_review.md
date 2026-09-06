# Security and Production-Readiness Review

1. Risk: PostgreSQL and Redis host port exposure. Impact: local users or accidental firewall changes could reach internal services. Implemented fix: only NGINX publishes a host port. Verify: `python validate.py --project barq-assessment --wait 120`.

2. Risk: Flat container network. Impact: the proxy could reach databases directly if compromised. Implemented fix: NGINX is on `frontend` only; dependencies are on internal `backend`. Verify: validation network checks and `docker network inspect barq-assessment_backend`.

3. Risk: Running the app container as root. Impact: a Flask vulnerability would have stronger container privileges. Implemented fix: `Dockerfile` creates and uses UID/GID 10001. Verify: `docker compose exec app-01 id`.

4. Risk: Mutable images. Impact: rebuilds could silently pull different base images. Implemented fix: Python, PostgreSQL, Redis, and NGINX images are pinned by digest. Verify: `docker compose -p barq-assessment config`.

5. Risk: Secrets in committed files. Impact: real credentials could leak. Implemented status: `.env` is ignored and `.env.example` contains only disposable lab values. Limitation: the lab password is visible for assessment reproducibility and must not be reused. Production follow-up: Docker secrets or an external secret manager.

6. Risk: Missing database backup. Impact: a volume mistake can delete records. Implemented fix: `backup.sh` and `restore.sh` use `pg_dump`/`pg_restore`. Verify: create a record, run backup, restore, and list `/records`.

7. Risk: Redis data loss. Impact: the shared counter could reset unexpectedly. Implemented fix: Redis AOF persistence and a named `redis-data` volume. Verify: restart Redis and call `/counter`.

8. Risk: Weak observability. Impact: failures are hard to correlate across NGINX and Flask. Implemented fix: request IDs and instance IDs are returned/logged. Verify: curl with `X-Request-ID` and inspect Docker logs.

9. Risk: Single NGINX, PostgreSQL, and Redis instances. Impact: these remain single points of failure. Implemented status: documented limitation for the lab. Production follow-up: redundant ingress, managed PostgreSQL HA, Redis HA/Sentinel/cluster, and tested failover.

10. Risk: Flask development server. Impact: it is not a production WSGI server. Implemented status: acceptable for the assessment contract; Docker image includes gunicorn but app command remains simple for lab visibility. Production follow-up: run gunicorn with health-aware worker settings.