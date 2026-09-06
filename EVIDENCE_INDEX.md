# Video Evidence Index

This document maps the required assessment tasks to their exact timestamps in the final demonstration video.

## 1. Initial State & Basic Verification
- **Initial docker compose up -d & ps output:** [MM:SS]
- **Testing Endpoints (/health, /ready):** [MM:SS]
- **Load Balancing Verification (hitting both instances):** [MM:SS]

## 2. Resilience & High Availability
- **Simulating Node Failure (docker compose stop app-01):** [MM:SS]
- **Proving zero-downtime (continuous requests to NGINX):** [MM:SS]
- **Recovery (docker compose start app-01):** [MM:SS]

## 3. Data Persistence (PostgreSQL & Redis)
- **Creating new records (POST /records):** [MM:SS]
- **Testing Persistence (Complete down and up cycle):** [MM:SS]
- **Validating records persist after restart:** [MM:SS]

## 4. Diagnostics & Troubleshooting
- **Executing video_challenge.sh:** [MM:SS]
- **Diagnosing the broken state:** [MM:SS]
- **Applying the fix and verifying recovery:** [MM:SS]

## 5. Scaling & Configuration Updates
- **Changing Public Port (8080 -> 8090):** [MM:SS]
- **Adding app-03 to docker-compose.yml:** [MM:SS]
- **Validating NGINX balancing across 3 instances:** [MM:SS]

## 6. Version Control & CI/CD
- **Reviewing git status and git diff:** [MM:SS]
- **Final git commit and git push:** [MM:SS]
- **Successful GitHub Actions CI Run:** [MM:SS]
