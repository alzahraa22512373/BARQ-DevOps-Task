# BARQ Assessment Environment

## Overview
This repository contains the hardened and fully operational Docker Compose environment for the BARQ Assessment. The architecture consists of a Python backend (scaled to two instances), a PostgreSQL database, a Redis cache, and an NGINX reverse proxy acting as a load balancer.

## Architecture
Please refer to \rchitecture.png\ for a visual representation of the system components and network topology.
- **Frontend Network:** NGINX Load Balancer (Port 8080)
- **Backend Network:** App-01, App-02, PostgreSQL, Redis

## Prerequisites
- Docker Engine & Docker Compose (v2+)
- PowerShell (for Windows environments) or Bash (Linux/macOS)

## Getting Started

1. **Environment Configuration:**
   Copy the example environment file and review the credentials (if necessary):
   \\\ash
   cp .env.example .env
   \\\

2. **Start the Environment:**
   Deploy the infrastructure in detached mode:
   \\\ash
   docker compose up -d
   \\\

3. **Verify Health:**
   Check if all containers are healthy:
   \\\ash
   docker compose ps
   \\\

4. **Testing the Endpoints:**
   - Base Route: \curl http://localhost:8080/\
   - Readiness Probe: \curl http://localhost:8080/ready\
   - Increment Counter (Redis): \curl http://localhost:8080/counter\
   - Fetch Records (PostgreSQL): \curl http://localhost:8080/records\

5. **Stop and Cleanup:**
   To spin down the environment while preserving data:
   \\\ash
   docker compose down
   \\\
   *(To wipe database volumes, append \-v\)*

## Documentation Index
- [Architecture Decisions](decisions.md)
- [Security Review](security_review.md)
- [Troubleshooting Guide](troubleshooting.md)
- [Log Analysis](log_analysis.md)
- [AI Usage](AI_USAGE.md)
- [Evidence Index](EVIDENCE_INDEX.md)
