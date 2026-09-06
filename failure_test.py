#!/usr/bin/env python3
"""Stop one backend, measure public traffic during failure, restore it, and verify recovery."""
import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request


def compose(project, *args, timeout=60):
    result = subprocess.run(
        ["docker", "compose", "-p", project, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def get_json(url, timeout=3):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.getcode(), json.loads(response.read().decode() or "{}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode() or "{}"
        try:
            return exc.code, json.loads(body)
        except json.JSONDecodeError:
            return exc.code, {"raw": body}
    except Exception as exc:
        return 0, {"error": type(exc).__name__}


def wait_for_instance(base_url, instance, seconds=60):
    deadline = time.time() + seconds
    while time.time() < deadline:
        status, body = get_json(base_url.rstrip("/") + "/instance")
        if status == 200 and body.get("instance_id") == instance:
            return True
        time.sleep(1)
    return False


def wait_for_ready(base_url, seconds=60):
    deadline = time.time() + seconds
    while time.time() < deadline:
        status, body = get_json(base_url.rstrip("/") + "/ready")
        if status == 200 and body.get("status") == "ready":
            return True
        time.sleep(2)
    return False


def sample(base_url, count=30, delay=0.2):
    stats = {"success": 0, "errors": 0, "instances": set(), "statuses": {}}
    for _ in range(count):
        status, body = get_json(base_url.rstrip("/") + "/instance")
        stats["statuses"][status] = stats["statuses"].get(status, 0) + 1
        if status == 200:
            stats["success"] += 1
            stats["instances"].add(body.get("instance_id"))
        else:
            stats["errors"] += 1
        time.sleep(delay)
    return stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="barq-assessment")
    parser.add_argument("--url", default="http://127.0.0.1:8080")
    parser.add_argument("--service", default="app-01", choices=("app-01", "app-02"))
    args = parser.parse_args()
    stopped = False
    try:
        if not wait_for_ready(args.url, 60):
            raise RuntimeError("environment did not start ready")
        print(f"Stopping {args.service}...")
        compose(args.project, "stop", args.service)
        stopped = True
        during = sample(args.url)
        during["instances"] = sorted(during["instances"])
        print("During failure:", json.dumps(during, sort_keys=True))
        if during["success"] == 0:
            raise RuntimeError("public traffic had no successful responses while one backend was stopped")
        if during["errors"] == 0:
            print("WARN: no public errors observed during the sample window")
        print(f"Starting {args.service}...")
        compose(args.project, "start", args.service)
        stopped = False
        if not wait_for_instance(args.url, args.service, 90):
            raise RuntimeError(f"{args.service} did not serve traffic after restart")
        if not wait_for_ready(args.url, 60):
            raise RuntimeError("environment did not return to ready")
        after = sample(args.url, count=12, delay=0.1)
        after["instances"] = sorted(after["instances"])
        print("After recovery:", json.dumps(after, sort_keys=True))
        print("PASS: failure/recovery behavior verified")
        return 0
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        if stopped:
            try:
                compose(args.project, "start", args.service)
            except Exception as cleanup_exc:
                print(f"WARN: cleanup start failed: {cleanup_exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())