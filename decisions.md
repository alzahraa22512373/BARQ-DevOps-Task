# Engineering Decisions & Architecture Trade-offs

## Overview
This document outlines the core architectural decisions, design patterns, and trade-offs made during the implementation and hardening of the BARQ Assessment environment.

---

## 1. Multi-Instance Application with NGINX Load Balancing
- **Decision:** Deployed two identical backend application instances (pp-01 and pp-02) fronted by an NGINX reverse proxy configured for round-robin load balancing.
- **Rationale:** Simulates a production-grade high-availability environment. Ensures that maintenance, failure testing (stopping one container), or updates can occur with zero total service downtime.
- **Trade-Offs:** Slightly higher memory consumption (~256MB per instance) compared to a single-instance setup. However, the gains in fault tolerance and horizontal scalability far outweigh the resource cost.

---

## 2. PostgreSQL and Redis Persistence Strategy
- **Decision:** Utilized Docker named volumes (postgres-data and edis-data) for stateful services, coupled with initialization scripts (init.sql) for database schema bootstrapping.
- **Rationale:** Named volumes ensure data durability across container lifecycles (e.g., docker compose down without -v), separating container compute from persistent storage managed by the Docker engine.
- **Trade-Offs:** Requires explicit management of Docker volumes during clean uninstalls, but completely prevents accidental data loss during container recreation or restart cycles.

---

## 3. Secret Management & Configuration Security
- **Decision:** Eliminated hard-coded credentials in docker-compose.yml by migrating sensitive values (such as database passwords) to environment variables injected via .env files, accompanied by an explicit .env.example template.
- **Rationale:** Adheres to the Twelve-Factor App methodology and security best practices, preventing credentials from leaking into version control repositories.
- **Trade-Offs:** Requires developers or operators to manually configure a local .env file prior to deployment, which is mitigated by clear documentation and the .env.example template.

---

## 4. Strict Healthchecks & Startup Ordering
- **Decision:** Configured robust healthchecks for PostgreSQL (pg_isready), Redis (edis-cli ping), and the Python application (/health endpoint), enforcing condition: service_healthy in depends_on.
- **Rationale:** Eliminates race conditions where application instances attempt to connect to databases or caches before they are fully initialized and ready to accept traffic.
- **Trade-Offs:** Slightly increases container startup time (due to healthcheck intervals and start periods), but guarantees absolute stability and eliminates crash-loop behaviors on boot.
