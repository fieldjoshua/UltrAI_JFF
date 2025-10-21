import json
from pathlib import Path
import pytest
from starlette.testclient import TestClient
from ultrai.api import app


@pytest.mark.pr11
def test_health_matches_contract():
    contract_path = Path("contracts/api/health.contract.json")
    assert contract_path.exists(), "health.contract.json missing"

    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    expected_status = contract.get("response", {}).get("status", 200)

    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == expected_status
        data = r.json()

    # Minimal contract: required keys and enum values
    schema = contract.get("response", {}).get("schema", {})
    required = schema.get("required", [])
    properties = schema.get("properties", {})

    for key in required:
        assert key in data, f"Missing required key: {key}"

    for key, prop in properties.items():
        if "enum" in prop and key in data:
            assert data[key] in prop["enum"], (
                "Invalid value for {}: {!r} not in {}".format(
                    key, data[key], prop["enum"]
                )
            )
