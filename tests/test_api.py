"""
Real integration tests for PR 11 API endpoints (NO MOCKS).
"""
import os
import time
import pytest
from pathlib import Path

import httpx


skip_if_no_api_key = pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set",
)


@pytest.mark.pr11
@skip_if_no_api_key
def test_health_local_uvicorn(tmp_path, monkeypatch):
    # Assumes local run: uvicorn ultrai.api:app --port 8000
    base = os.getenv("ULTRAI_API_BASE", "http://127.0.0.1:8000")
    r = httpx.get(f"{base}/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


@pytest.mark.pr11
@skip_if_no_api_key
def test_runs_and_status_progress(monkeypatch):
    base = os.getenv("ULTRAI_API_BASE", "http://127.0.0.1:8000")

    # Start a real run
    payload = {"query": "What is 2+2?", "cocktail": "SPEEDY"}
    r = httpx.post(f"{base}/runs", json=payload, timeout=30)
    assert r.status_code == 200
    run_id = r.json()["run_id"]

    # Give the API a moment to start processing
    time.sleep(2)

    # Poll status until final or timeout
    deadline = time.time() + 180
    last_phase = None
    while time.time() < deadline:
        s = httpx.get(f"{base}/runs/{run_id}/status", timeout=30)
        assert s.status_code == 200
        data = s.json()
        last_phase = data.get("phase")
        if data.get("completed"):
            break
        time.sleep(5)

    assert data.get("completed") is True, (
        f"Pipeline did not complete, last phase={last_phase}"
    )
    # Verify artifacts
    a = httpx.get(f"{base}/runs/{run_id}/artifacts", timeout=30)
    assert a.status_code == 200
    files = a.json().get("files", [])
    required = [
        "00_ready.json",
        "01_inputs.json",
        "02_activate.json",
        "03_initial.json",
        "04_meta.json",
        "05_ultrai.json",
    ]
    present = {Path(f).name for f in files}
    for req in required:
        assert req in present, f"Missing artifact: {req}"
