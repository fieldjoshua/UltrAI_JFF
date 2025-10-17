"""
Integration Tests - Full Workflow

REAL integration tests (NO MOCKS) that verify multiple phases work together.
Tests the complete flow from system readiness through user input collection.
"""

import pytest
import json
import os
from pathlib import Path
from ultrai.system_readiness import check_system_readiness
from ultrai.user_input import collect_user_inputs, load_inputs


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set - integration test requires actual API key"
)
@pytest.mark.asyncio
async def test_full_workflow_pr01_through_pr02(tmp_path, monkeypatch):
    """
    Integration test: Full workflow from system readiness to user input collection

    REAL INTEGRATION TEST - Tests complete flow:
    1. System readiness check (PR 01) - creates 00_ready.json
    2. User input collection (PR 02) - creates 01_inputs.json
    3. Verify both artifacts exist and contain correct data
    4. Verify data can be loaded and accessed from both phases
    """
    monkeypatch.chdir(tmp_path)
    run_id = "integration_test_001"

    # Phase 1: System Readiness (PR 01)
    print("\n=== Phase 1: System Readiness ===")
    readiness_result = await check_system_readiness(run_id=run_id)

    assert "readyList" in readiness_result
    assert len(readiness_result["readyList"]) >= 2, "Need at least 2 ready LLMs"

    ready_artifact = Path(f"runs/{run_id}/00_ready.json")
    assert ready_artifact.exists(), "00_ready.json not created"

    with open(ready_artifact, "r") as f:
        ready_data = json.load(f)
    print(f"✓ System ready with {len(ready_data['readyList'])} LLMs")

    # Phase 2: User Input Collection (PR 02)
    print("\n=== Phase 2: User Input Collection ===")
    inputs_result = collect_user_inputs(
        query="What are the advantages of multi-LLM synthesis?",
        analysis="Synthesis",
        cocktail="PREMIUM",
        run_id=run_id
    )

    assert inputs_result["QUERY"] == "What are the advantages of multi-LLM synthesis?"
    assert inputs_result["COCKTAIL"] == "PREMIUM"
    assert len(inputs_result["ADDONS"]) == 0

    inputs_artifact = Path(f"runs/{run_id}/01_inputs.json")
    assert inputs_artifact.exists(), "01_inputs.json not created"

    with open(inputs_artifact, "r") as f:
        inputs_data = json.load(f)
    print(f"✓ User inputs collected: {inputs_data['COCKTAIL']} cocktail with {len(inputs_data['ADDONS'])} add-ons")

    # Phase 3: Verify both artifacts are accessible
    print("\n=== Phase 3: Cross-Phase Access ===")

    # Load inputs using load_inputs function
    loaded_inputs = load_inputs(run_id)
    assert loaded_inputs["QUERY"] == inputs_result["QUERY"]
    assert loaded_inputs["COCKTAIL"] == inputs_result["COCKTAIL"]
    print("✓ Inputs can be loaded from artifact")

    # Verify both artifacts exist in same run directory
    run_dir = Path(f"runs/{run_id}")
    assert run_dir.exists()
    assert (run_dir / "00_ready.json").exists()
    assert (run_dir / "01_inputs.json").exists()
    print(f"✓ Both artifacts exist in runs/{run_id}/")

    # Verify data consistency
    assert ready_data["run_id"] == run_id  # PR 01 has run_id at top level
    assert inputs_data["metadata"]["run_id"] == run_id  # PR 02 has run_id in metadata
    print("✓ Run IDs consistent across phases")

    print("\n=== Integration Test PASSED ===")
    print(f"Complete workflow validated: System ready → User inputs collected → Artifacts accessible")


@pytest.mark.integration
def test_can_access_all_cocktails(tmp_path, monkeypatch):
    """
    Test that all 4 cocktail choices can be accessed and used

    REAL TEST - Verifies all cocktail options are accessible
    """
    monkeypatch.chdir(tmp_path)

    cocktails = ["PREMIUM", "SPEEDY", "BUDGET", "DEPTH"]

    for cocktail in cocktails:
        run_id = f"cocktail_test_{cocktail.lower()}"

        result = collect_user_inputs(
            query=f"Test query for {cocktail}",
            cocktail=cocktail,
            run_id=run_id
        )

        assert result["COCKTAIL"] == cocktail

        # Verify artifact can be accessed
        artifact_path = Path(f"runs/{run_id}/01_inputs.json")
        assert artifact_path.exists()

        # Load and verify
        loaded = load_inputs(run_id)
        assert loaded["COCKTAIL"] == cocktail

    print(f"\n✓ All {len(cocktails)} cocktails accessible and working")


@pytest.mark.skip(reason="Add-ons functionality has been removed")
@pytest.mark.integration
def test_can_access_all_addons(tmp_path, monkeypatch):
    """
    Test that all 5 add-ons can be accessed and used

    REAL TEST - Verifies all add-on options are accessible
    """
    monkeypatch.chdir(tmp_path)

    from ultrai.user_input import AVAILABLE_ADDONS

    # Test selecting all add-ons at once
    result = collect_user_inputs(
        query="Test query with all add-ons",
        cocktail="PREMIUM",
        run_id="all_addons_test"
    )

    assert len(result["ADDONS"]) == len(AVAILABLE_ADDONS)

    for addon in AVAILABLE_ADDONS:
        assert addon in result["ADDONS"], f"Add-on {addon} not accessible"

    # Verify artifact persists all add-ons
    loaded = load_inputs("all_addons_test")
    assert len(loaded["ADDONS"]) == len(AVAILABLE_ADDONS)

    print(f"\n✓ All {len(AVAILABLE_ADDONS)} add-ons accessible: {', '.join(AVAILABLE_ADDONS)}")


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set - integration test requires actual API key"
)
@pytest.mark.asyncio
async def test_multiple_runs_with_different_configs(tmp_path, monkeypatch):
    """
    Test that multiple runs can be created with different configurations

    REAL INTEGRATION TEST - Verifies system can handle multiple concurrent runs
    """
    monkeypatch.chdir(tmp_path)

    configs = [
        {"run_id": "run_premium", "cocktail": "PREMIUM"},
        {"run_id": "run_speedy", "cocktail": "SPEEDY"},
        {"run_id": "run_budget", "cocktail": "BUDGET"},
    ]

    for config in configs:
        # System readiness
        ready = await check_system_readiness(run_id=config["run_id"])
        assert len(ready["readyList"]) >= 2

        # User inputs
        inputs = collect_user_inputs(
            query=f"Test query for {config['cocktail']}",
            cocktail=config["cocktail"],
            run_id=config["run_id"]
        )

        assert inputs["COCKTAIL"] == config["cocktail"]
        assert inputs["ADDONS"] == []

    # Verify all runs are isolated and accessible
    for config in configs:
        run_dir = Path(f"runs/{config['run_id']}")
        assert run_dir.exists()
        assert (run_dir / "00_ready.json").exists()
        assert (run_dir / "01_inputs.json").exists()

        loaded = load_inputs(config["run_id"])
        assert loaded["COCKTAIL"] == config["cocktail"]

    print(f"\n✓ {len(configs)} independent runs created and accessible")


@pytest.mark.integration
def test_run_directory_structure(tmp_path, monkeypatch):
    """
    Test that the runs directory structure is correct and accessible

    REAL TEST - Verifies artifacts are organized properly
    """
    monkeypatch.chdir(tmp_path)

    run_id = "structure_test"

    # Create inputs (which creates the run directory)
    collect_user_inputs(
        query="Test query",
        cocktail="PREMIUM",
        run_id=run_id
    )

    # Verify structure
    runs_dir = Path("runs")
    assert runs_dir.exists(), "runs/ directory not created"
    assert runs_dir.is_dir()

    run_dir = runs_dir / run_id
    assert run_dir.exists(), f"runs/{run_id}/ not created"
    assert run_dir.is_dir()

    # Verify artifact naming convention (00_, 01_ prefixes)
    artifacts = list(run_dir.glob("*.json"))
    assert len(artifacts) > 0, "No artifacts in run directory"

    # Check that artifacts follow naming convention
    artifact_names = [a.name for a in artifacts]
    assert any(name.startswith("0") for name in artifact_names), "Artifacts don't follow 00_, 01_ naming convention"

    print(f"\n✓ Directory structure correct: runs/{run_id}/ with properly named artifacts")


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set - integration test requires actual API key"
)
@pytest.mark.asyncio
async def test_readiness_data_accessible_for_cocktail_matching(tmp_path, monkeypatch):
    """
    Test that readiness data (PR 01) can be accessed for cocktail matching (future PR 03)

    REAL INTEGRATION TEST - Verifies PR 01 data is usable by future PR 03
    This tests the data flow that PR 03 will need
    """
    monkeypatch.chdir(tmp_path)
    run_id = "pr03_prep_test"

    # Get system readiness
    await check_system_readiness(run_id=run_id)

    # Get user cocktail selection
    collect_user_inputs(
        query="Test query",
        cocktail="PREMIUM",
        run_id=run_id
    )

    # Verify PR 03 will have access to both pieces of data
    ready_artifact = Path(f"runs/{run_id}/00_ready.json")
    inputs_artifact = Path(f"runs/{run_id}/01_inputs.json")

    assert ready_artifact.exists()
    assert inputs_artifact.exists()

    # Load both artifacts (simulating what PR 03 will do)
    with open(ready_artifact, "r") as f:
        ready_data = json.load(f)

    with open(inputs_artifact, "r") as f:
        inputs_data = json.load(f)

    # Verify PR 03 has all needed data
    assert "readyList" in ready_data
    assert "COCKTAIL" in inputs_data
    assert len(ready_data["readyList"]) >= 2
    assert inputs_data["COCKTAIL"] in ["PREMIUM", "SPEEDY", "BUDGET", "DEPTH"]

    print(f"\n✓ PR 03 will have access to:")
    print(f"  - {len(ready_data['readyList'])} ready LLMs from 00_ready.json")
    print(f"  - {inputs_data['COCKTAIL']} cocktail selection from 01_inputs.json")
    print(f"  - Ready for cocktail matching logic")
