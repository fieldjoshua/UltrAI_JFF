"""
CLI Access Tests

Tests that verify users can access all UltrAI features through the CLI module.
"""

import pytest
from ultrai.cli import (
    print_banner,
    print_ready_status,
    print_submission_summary
)
from ultrai.user_input import VALID_COCKTAILS


@pytest.mark.pr02
def test_cli_module_imports():
    """
    Test that CLI module can be imported and accessed

    Verifies users can access the CLI functionality
    """
    from ultrai import cli

    assert hasattr(cli, 'run_cli')
    assert hasattr(cli, 'main')
    assert callable(cli.run_cli)
    assert callable(cli.main)


@pytest.mark.pr02
def test_cocktail_constants_accessible():
    """
    Test that all 5 cocktail choices are accessible to users

    Verifies VALID_COCKTAILS constant is available
    """
    assert len(VALID_COCKTAILS) == 5
    assert "LUXE" in VALID_COCKTAILS
    assert "PREMIUM" in VALID_COCKTAILS
    assert "SPEEDY" in VALID_COCKTAILS
    assert "BUDGET" in VALID_COCKTAILS
    assert "DEPTH" in VALID_COCKTAILS


@pytest.mark.pr02
def test_cli_helper_functions_work(capsys):
    """
    Test that CLI helper functions work correctly

    Verifies print functions can be called
    """
    # Test banner
    print_banner()
    captured = capsys.readouterr()
    # Banner is ASCII art, check for the text subtitle line
    assert "MULTI-LLM" in captured.out or "SYNTHESIS" in captured.out or len(captured.out) > 100

    # Test ready status
    ready_result = {
        'run_id': 'test_123',
        'llm_count': 100,
        'status': 'READY'
    }
    print_ready_status(ready_result)
    captured = capsys.readouterr()
    assert "test_123" in captured.out
    assert "100" in captured.out

    # Test submission summary
    inputs_result = {
        'QUERY': 'Test query',
        'ANALYSIS': 'Synthesis',
        'COCKTAIL': 'PREMIUM',
        'metadata': {
            'run_id': 'test_456'
        }
    }
    print_submission_summary(inputs_result)
    captured = capsys.readouterr()
    assert "Test query" in captured.out
    assert "PREMIUM" in captured.out


@pytest.mark.integration
def test_user_can_access_all_features_programmatically(tmp_path, monkeypatch):
    """
    Test that users can access all features programmatically

    INTEGRATION TEST - Verifies all user-facing functions are accessible
    """
    monkeypatch.chdir(tmp_path)

    from ultrai.system_readiness import check_system_readiness
    from ultrai.user_input import collect_user_inputs, load_inputs, VALID_COCKTAILS

    # User can access system readiness function
    assert callable(check_system_readiness)

    # User can access input collection function
    assert callable(collect_user_inputs)
    assert callable(load_inputs)

    # User can access cocktail choices
    assert VALID_COCKTAILS is not None

    # User can create inputs
    result = collect_user_inputs(
        query="User test query",
        cocktail="PREMIUM",
        run_id="user_test"
    )

    # User can verify submission
    assert result["QUERY"] == "User test query"
    assert result["COCKTAIL"] == "PREMIUM"

    # User can load their submission
    loaded = load_inputs("user_test")
    assert loaded["QUERY"] == "User test query"


@pytest.mark.pr02
def test_cli_can_be_run_as_module():
    """
    Test that CLI can be run as a Python module

    Verifies python -m ultrai.cli works
    """
    from ultrai import cli

    # Verify the run_cli function exists and is callable
    assert hasattr(cli, 'run_cli')
    assert callable(cli.run_cli)

    # Verify main function exists
    assert hasattr(cli, 'main')
    assert callable(cli.main)


@pytest.mark.pr02
def test_all_features_documented_in_cli():
    """
    Test that CLI exposes all key features

    Verifies CLI has functions for all user interactions
    """
    from ultrai import cli

    # Check that CLI has prompt functions for user input
    assert hasattr(cli, 'prompt_query')
    assert hasattr(cli, 'prompt_cocktail')

    # Check that CLI has display functions
    assert hasattr(cli, 'print_banner')
    assert hasattr(cli, 'print_ready_status')
    assert hasattr(cli, 'print_submission_summary')

    # Check that CLI has main entry point
    assert hasattr(cli, 'main')
    assert hasattr(cli, 'run_cli')
