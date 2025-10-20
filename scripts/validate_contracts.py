#!/usr/bin/env python3
"""
Validate that backend responses satisfy minimal API contracts.

Currently validates only /health using contracts/api/health.contract.json.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

import httpx


def load_contract(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_response_against_contract(
    response_json: Dict[str, Any],
    contract: Dict[str, Any],
) -> Tuple[bool, str]:
    schema = contract.get("response", {}).get("schema", {})
    required = schema.get("required", [])
    properties = schema.get("properties", {})

    # Check required keys exist
    for key in required:
        if key not in response_json:
            return False, f"Missing required key: {key}"

    # Check enums if present
    for key, prop in properties.items():
        if "enum" in prop and key in response_json:
            if response_json[key] not in prop["enum"]:
                msg = (
                    "Invalid value for {}: {!r} not in {}".format(
                        key, response_json[key], prop["enum"]
                    )
                )
                return False, msg

    return True, "ok"


def main() -> int:
    base_dir = Path(__file__).resolve().parent.parent
    contracts_dir = base_dir / "contracts" / "api"

    health_contract_path = contracts_dir / "health.contract.json"
    if not health_contract_path.exists():
        print("health.contract.json not found; skipping")
        return 0

    contract = load_contract(health_contract_path)

    # Call backend /health (default prod URL)
    backend_url = "https://ultrai-jff.onrender.com"
    r = httpx.get(
        f"{backend_url}/health",
        timeout=10.0,
    )
    expected = contract.get("response", {}).get("status", 200)
    if r.status_code != expected:
        print(f"/health returned HTTP {r.status_code}")
        return 2

    ok, msg = validate_response_against_contract(r.json(), contract)
    if not ok:
        print(f"/health contract validation failed: {msg}")
        return 3

    print("/health contract OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
