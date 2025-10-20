#!/usr/bin/env python3
"""
Simple production health checker for UltrAI.

Checks:
- Backend health: GET /health
- Frontend load: GET /
- Optional: Artifact fetch for a specific run_id:
  GET /runs/{run_id}/artifacts/05_ultrai.json

Usage:
  . .venv/bin/activate && python scripts/prod_check.py \
      --backend-url https://ultrai-jff.onrender.com \
      --frontend-url https://ultrai-jff-frontend.onrender.com \
      [--run-id api_speedy_YYYYMMDD_HHMMSS]
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

import httpx


def check_backend_health(
    backend_url: str,
    timeout_s: float = 15.0,
) -> tuple[bool, str]:
    try:
        r = httpx.get(f"{backend_url}/health", timeout=timeout_s)
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"
        data = r.json()
        if data.get("status") == "ok":
            return True, "ok"
        return False, f"Unexpected payload: {data!r}"
    except Exception as e:  # noqa: BLE001
        return False, f"Exception: {type(e).__name__}: {e}"


def check_frontend_load(
    frontend_url: str,
    timeout_s: float = 15.0,
) -> tuple[bool, str]:
    try:
        r = httpx.get(frontend_url, timeout=timeout_s, follow_redirects=True)
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"
        html = r.text
        if '<div id="root"></div>' in html or '<div id="root"' in html:
            return True, "root present"
        return False, "root div missing"
    except Exception as e:  # noqa: BLE001
        return False, f"Exception: {type(e).__name__}: {e}"


def check_artifact(
    backend_url: str,
    run_id: str,
    timeout_s: float = 15.0,
) -> tuple[bool, str]:
    try:
        url = f"{backend_url}/runs/{run_id}/artifacts/05_ultrai.json"
        r = httpx.get(url, timeout=timeout_s)
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"
        # Ensure it's JSON and contains something plausible
        data = r.json()
        if isinstance(data, dict) and data:
            return True, "artifact ok"
        return False, "empty or non-dict JSON"
    except Exception as e:  # noqa: BLE001
        return False, f"Exception: {type(e).__name__}: {e}"


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="UltrAI production health check"
    )
    parser.add_argument(
        "--backend-url",
        default="https://ultrai-jff.onrender.com",
        help="Backend base URL (default: %(default)s)",
    )
    parser.add_argument(
        "--frontend-url",
        default="https://ultrai-jff-frontend.onrender.com",
        help="Frontend base URL (default: %(default)s)",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Optional run_id to validate artifact fetch (05_ultrai.json)",
    )

    args = parser.parse_args(argv)

    be_ok, be_msg = check_backend_health(args.backend_url)
    fe_ok, fe_msg = check_frontend_load(args.frontend_url)

    print(
        f"Backend /health: {'OK' if be_ok else 'FAIL'} - {be_msg}"
    )
    print(
        f"Frontend load : {'OK' if fe_ok else 'FAIL'} - {fe_msg}"
    )

    rc = 0 if (be_ok and fe_ok) else 1

    if args.run_id:
        art_ok, art_msg = check_artifact(
            args.backend_url, args.run_id
        )
        print(
            "Artifact 05_ultrai.json ({}): {} - {}".format(
                args.run_id, "OK" if art_ok else "FAIL", art_msg
            )
        )
        if not art_ok:
            rc = 2 if rc == 0 else rc

    return rc


if __name__ == "__main__":
    sys.exit(main())
