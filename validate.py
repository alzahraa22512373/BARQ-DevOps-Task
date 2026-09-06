#!/usr/bin/env python3
"""Validate the repaired BARQ Docker environment through the public NGINX port."""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

SERVICES = ("app-01", "app-02", "nginx", "postgres", "redis")


def docker_json(*args):
    result = subprocess.run(["docker", *args], capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return json.loads(result.stdout)


def request_json(base_url, path, method="GET", body=None, expected=200, timeout=5):
    data = None
    headers = {"X-Request-ID": "validate"}
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(base_url.rstrip("/") + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            payload = response.read()
            status = response.getcode()
            response_headers = dict(response.headers)
    except urllib.error.HTTPError as exc:
        payload = exc.read()
        status = exc.code
        response_headers = dict(exc.headers)
    parsed = json.loads(payload.decode() or "{}")
    if status != expected:
        raise AssertionError(f"{path} returned {status}, expected {expected}: {parsed}")
    if "X-Request-ID" not in response_headers:
        raise AssertionError(f"{path} did not return X-Request-ID")
    return parsed, response_headers


def wait_for_ready(base_url, seconds):
    deadline = time.time() + seconds
    last_error = None
    while time.time() < deadline:
        try:
            body, _ = request_json(base_url, "/ready")
            if body.get("status") == "ready":
                return
        except Exception as exc:
            last_error = exc
        time.sleep(2)
    raise TimeoutError(f"environment was not ready within {seconds}s: {last_error}")


def check_container_health(project):
    containers = {}
    for service in SERVICES:
        info = docker_json("inspect", service)[0]
        labels = info.get("Config", {}).get("Labels", {})
        if labels.get("com.docker.compose.project") != project:
            raise AssertionError(f"{service} is not owned by Compose project {project}")
        state = info["State"]
        if not state.get("Running"):
            raise AssertionError(f"{service} is not running")
        health = state.get("Health", {}).get("Status")
        if health and health != "healthy":
            raise AssertionError(f"{service} health is {health}")
        containers[service] = info
    return containers


def check_ports(containers, public_port):
    for service in ("app-01", "app-02", "postgres", "redis"):
        ports = containers[service]["NetworkSettings"].get("Ports") or {}
        published = {key: value for key, value in ports.items() if value}
        if published:
            raise AssertionError(f"{service} exposes host ports: {published}")
    nginx_ports = containers["nginx"]["NetworkSettings"].get("Ports") or {}
    binding = (nginx_ports.get("80/tcp") or [{}])[0]
    if binding.get("HostIp") != "127.0.0.1" or binding.get("HostPort") != str(public_port):
        raise AssertionError(f"nginx is not bound to 127.0.0.1:{public_port}: {nginx_ports}")


def network_names(info):
    return set(info["NetworkSettings"]["Networks"])


def check_networks(containers):
    frontend = [name for name in network_names(containers["app-01"]) if name.endswith("frontend")]
    backend = [name for name in network_names(containers["app-01"]) if name.endswith("backend")]
    if len(frontend) != 1 or len(backend) != 1:
        raise AssertionError("app-01 must be on one frontend and one backend network")
    expected = {
        "app-01": set(frontend + backend),
        "app-02": set(frontend + backend),
        "nginx": set(frontend),
        "postgres": set(backend),
        "redis": set(backend),
    }
    for service, networks in expected.items():
        actual = network_names(containers[service])
        if actual != networks:
            raise AssertionError(f"{service} networks are {actual}, expected {networks}")
    backend_info = docker_json("network", "inspect", backend[0])[0]
    if not backend_info.get("Internal"):
        raise AssertionError("backend network must be internal")


def check_http_contract(base_url):
    root, _ = request_json(base_url, "/")
    if not root.get("message") or not root.get("instance_id"):
        raise AssertionError("/ must include message and instance_id")
    request_json(base_url, "/health")
    request_json(base_url, "/ready")
    request_json(base_url, "/missing", expected=404)
    request_json(base_url, "/records", method="POST", body={"title": ""}, expected=400)
    created, _ = request_json(base_url, "/records", method="POST", body={"title": "Validation proof"}, expected=201)
    records, _ = request_json(base_url, "/records")
    if created["record"] not in records["records"]:
        raise AssertionError("created PostgreSQL record was not listed")
    first, _ = request_json(base_url, "/counter")
    second, _ = request_json(base_url, "/counter")
    if int(second["counter"]) <= int(first["counter"]):
        raise AssertionError("Redis counter did not increase")
    seen = set()
    for _ in range(40):
        body, headers = request_json(base_url, "/instance")
        if headers.get("X-Instance-ID") != body.get("instance_id"):
            raise AssertionError("/instance header does not match body")
        seen.add(body["instance_id"])
        if seen == {"app-01", "app-02"}:
            return
    raise AssertionError(f"did not see both backends through nginx; saw {seen}")


def run_step(name, func):
    try:
        func()
    except Exception as exc:
        print(f"FAIL: {name}: {exc}")
        return False
    print(f"PASS: {name}")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="barq-assessment")
    parser.add_argument("--url", default=None)
    parser.add_argument("--wait", type=int, default=60)
    args = parser.parse_args()
    public_port = os.getenv("PUBLIC_PORT", "8080")
    base_url = args.url or f"http://127.0.0.1:{public_port}"
    containers = {}
    ok = True
    ok &= run_step("public readiness", lambda: wait_for_ready(base_url, args.wait))

    def inspect():
        nonlocal containers
        containers = check_container_health(args.project)

    ok &= run_step("container health", inspect)
    ok &= run_step("host port policy", lambda: check_ports(containers, public_port))
    ok &= run_step("network isolation", lambda: check_networks(containers))
    ok &= run_step("HTTP/API contract", lambda: check_http_contract(base_url))
    if not ok:
        print("\nEnvironment validation FAILED.")
        return 1
    print("\nEnvironment validation PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())