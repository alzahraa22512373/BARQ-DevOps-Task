# Troubleshooting Journal

## 1. Wrong application bind address and health path
- Symptom: App containers could run but NGINX could not reliably reach them; healthchecks used `/healthz`.
- Hypothesis: The Flask process was bound to localhost or the healthcheck path did not match the contract.
- Command or test: `docker compose -p barq-assessment logs --no-color app-01 app-02`, `docker inspect app-01`.
- Result: The app contract exposes `/health`; Compose originally referenced the wrong path and starter values.
- Root cause: Incorrect starter environment/healthcheck values.
- Fix: Set `APP_HOST=0.0.0.0`, `APP_PORT=8080`, and healthcheck `/health`.
- Retest: `python -m unittest discover -s tests -v`, `python validate.py --project barq-assessment --wait 120`.

## 2. PostgreSQL state was not persisted correctly
- Symptom: The starter Compose mounted the named volume at the wrong PostgreSQL path and used tmpfs for active data.
- Hypothesis: Records would disappear when the database container was recreated.
- Command or test: Review `docker-compose.yml`; create/list records through `/records`.
- Root cause: PostgreSQL active data directory was not backed by the named volume.
- Fix: Mount `postgres-data:/var/lib/postgresql/data` and keep `database/init.sql` as read-only initialization input.
- Retest: `curl /records`, restart/recreate containers while keeping the volume, list records again.

## 3. PostgreSQL and Redis were exposed to the host
- Symptom: Compose published database/cache ports to `127.0.0.1`.
- Hypothesis: This violates the requirement to publish only NGINX.
- Command or test: `docker compose -p barq-assessment config`, `python validate.py --project barq-assessment --wait 120`.
- Root cause: Starter port mappings were left on internal services.
- Fix: Remove host `ports` from PostgreSQL and Redis.
- Retest: Validation host port policy passed.

## 4. Duplicate backend identity
- Symptom: Both app services could return the same `instance_id`.
- Hypothesis: `app-02` inherited or repeated `INSTANCE_ID=app-01`.
- Command or test: Repeated `curl http://127.0.0.1:8080/instance`.
- Root cause: Incorrect Compose environment for the second app container.
- Fix: Set `INSTANCE_ID=app-02` for `app-02`.
- Retest: Validation saw both `app-01` and `app-02` through NGINX.

## 5. App healthcheck was too slow on Docker Desktop
- Symptom: Compose reported app containers as unhealthy even though Flask logs showed the server was listening.
- Hypothesis: The healthcheck command using Python exceeded the short Docker timeout on this workstation.
- Command or test: `docker inspect app-01 --format '{{json .State.Health}}'`.
- Result: Health check exceeded timeout.
- Fix: Keep the same `/health` check but use bounded, longer `timeout`, `retries`, and `start_period`.
- Retest: `app-01` and `app-02` became healthy, then `validate.py` passed.

## 6. Failure test behavior
- Symptom: Stopping one backend caused a mix of successful responses and temporary 502/timeouts.
- Command or test: `python failure_test.py --project barq-assessment --url http://127.0.0.1:8080`.
- Result: During failure, traffic still had successful responses from the surviving backend; after recovery both instances served traffic.
- Limitation: Some client-visible errors remain because NGINX is configured with `proxy_next_upstream off` to make the failure visible for the assessment.