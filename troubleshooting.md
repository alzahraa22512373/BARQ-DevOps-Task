# Troubleshooting & Diagnostics Guide

## 1. NGINX 502 Bad Gateway during Startup
- **Symptom:** Accessing http://localhost:8080/ immediately after docker compose up -d returned a 502 Bad Gateway error.
- **Diagnosis:** NGINX started and attempted to route traffic to pp-01 and pp-02 before the Python application servers were fully initialized and bound to their listening ports.
- **Resolution:** Implemented depends_on with condition: service_healthy for the NGINX service, forcing it to wait until the application containers successfully pass their /health checks before starting the proxy.

## 2. Ephemeral Database State (Data Loss on Restart)
- **Symptom:** Records created via POST requests to /records were entirely lost after executing docker compose down followed by docker compose up -d.
- **Diagnosis:** PostgreSQL was writing its active data to the container's ephemeral filesystem instead of a persistent host volume.
- **Resolution:** Configured Docker named volumes (postgres-data:/var/lib/postgresql/data) in docker-compose.yml to ensure data persistence across container lifecycle events.

## 3. Application Crash Loop: Database Connection Refused
- **Symptom:** pp-01 continuously restarted and outputted psycopg2.OperationalError: Connection refused in the logs.
- **Diagnosis:** The Python application attempted to establish a database connection while PostgreSQL was still bootstrapping its system tables and not yet accepting remote connections.
- **Resolution:** Added a robust healthcheck to the PostgreSQL container using pg_isready and strictly enforced the application's startup sequence to wait for the database to become healthy.
