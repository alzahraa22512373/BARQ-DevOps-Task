# Evidence Index

Fill the placeholders during/after the final video and GitHub push.

- Repository URL: TODO
- Final commit: TODO
- Matching CI run: TODO
- Continuous 12-18 minute video URL: TODO
- Challenge receipt ID: TODO, from `.assessment/challenge.json` after running `./video_challenge.sh` once in the video.
- Starting video commit: TODO
- Later documentation-only commits, if any: TODO or None

## Requirement Map

| Requirement | File or command evidence | Commit | Video timestamp |
| --- | --- | --- | --- |
| Two Flask instances behind NGINX | `docker-compose.yml`, `nginx/nginx.conf`, `curl /instance` loop | TODO | TODO |
| PostgreSQL and Redis real dependencies | `app/server.py`, `database/init.sql`, `curl /records`, `curl /counter` | TODO | TODO |
| Only NGINX publishes host port | `docker-compose.yml`, `python validate.py --project barq-assessment --wait 120` | TODO | TODO |
| frontend/backend network isolation | `docker-compose.yml`, `validate.py` network checks | TODO | TODO |
| Distinct instance IDs | `curl http://127.0.0.1:8080/instance` repeated | TODO | TODO |
| Health and readiness semantics | `tests/test_app.py`, `curl /health`, `curl /ready` | TODO | TODO |
| Validation automation | `validate.py` output | TODO | TODO |
| Failure/recovery automation | `failure_test.py` output | TODO | TODO |
| PostgreSQL backup/restore | `backup.sh`, `restore.sh`, `/records` before/after | TODO | TODO |
| CI pipeline | `.github/workflows/ci.yml`, GitHub Actions URL | TODO | TODO |
| Historical log analysis | `log_analysis.md` | TODO | TODO |
| Troubleshooting journal | `troubleshooting.md` | TODO | TODO |
| Decisions | `decisions.md` | TODO | TODO |
| Security review | `security_review.md` | TODO | TODO |
| AI disclosure | `AI_USAGE.md` | TODO | TODO |
| Architecture diagram | `architecture.png` | TODO | TODO |
| Live port change to 8090 | edit `.env` or set `PUBLIC_PORT=8090`, recreate NGINX, curl port 8090 | TODO | TODO |
| Live third app instance | add `app-03`, update `nginx.conf`, rerun validation with `--url http://127.0.0.1:8090` | TODO | TODO |

## Local Verification Already Run

```text
python -m unittest discover -s tests -v -> OK, 8 tests
python validate.py --project barq-assessment --wait 120 -> PASSED
python failure_test.py --project barq-assessment --url http://127.0.0.1:8080 -> PASSED
```

The final submission must replace TODO values with actual commit hashes, links, and video timestamps.