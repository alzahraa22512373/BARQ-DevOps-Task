# AI Usage

AI assistance was used for code review, troubleshooting, script drafting, and documentation structure. The user retained ownership of the final commands, video evidence, and submission.

## Assisted Areas

- Reviewed the application contract and separated it from the user request.
- Identified Docker/NGINX/networking issues in `docker-compose.yml` and `nginx/nginx.conf`.
- Drafted and refined `validate.py`, `failure_test.py`, `backup.sh`, `restore.sh`, and `.github/workflows/ci.yml`.
- Helped prepare documentation in `README.md`, `troubleshooting.md`, `log_analysis.md`, `decisions.md`, and `security_review.md`.

## Verification

- Ran `python -m unittest discover -s tests -v` successfully.
- Ran `docker compose -p barq-assessment config --quiet` successfully.
- Ran `python validate.py --project barq-assessment --wait 120` successfully.
- Ran `python failure_test.py --project barq-assessment --url http://127.0.0.1:8080` successfully.

## Limits

AI did not fabricate GitHub URLs, commit hashes, CI run links, or video timestamps. Those must be filled from the actual repository, CI run, and recorded video.