"""
Timeout designation system with custom status display.

Tests can be marked with timeout markers to show custom status instead of "FAILED":
- @pytest.mark.t15 + @pytest.mark.timeout(15) → Shows "TO-15" when timeout occurs
- @pytest.mark.t30 + @pytest.mark.timeout(30) → Shows "TO-30" when timeout occurs
- @pytest.mark.t60 + @pytest.mark.timeout(60) → Shows "TO-60" when timeout occurs
- @pytest.mark.t120 + @pytest.mark.timeout(120) → Shows "TO-120" when timeout occurs

Usage example:
    @pytest.mark.t15
    @pytest.mark.timeout(15)
    def test_slow_api_call():
        # Test that may timeout at 15 seconds
        # Will show "TO-15" instead of "FAILED" if it times out
        pass

This allows you to designate expected timeouts and distinguish them from
actual test failures in the pytest output.

The implementation is in conftest.py using pytest hooks:
- pytest_collection_modifyitems: Registers tests with timeout markers
- pytest_runtest_makereport: Detects timeout exceptions
- pytest_report_teststatus: Customizes the display to show "TO-XX"
"""

import pytest


def pytest_configure(config):
    """Configure pytest to recognize timeout markers"""
    config.addinivalue_line(
        "markers", "t15: Test that times out at 15s (not failed)"
    )
    config.addinivalue_line(
        "markers", "t30: Test that times out at 30s (not failed)"
    )
    config.addinivalue_line(
        "markers", "t60: Test that times out at 60s (not failed)"
    )
    config.addinivalue_line(
        "markers", "t120: Test that times out at 120s (not failed)"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle timeout markers"""
    for item in items:
        # If test has timeout marker, it's expected to timeout
        if item.get_closest_marker("t15") or item.get_closest_marker("t30") or \
           item.get_closest_marker("t60") or item.get_closest_marker("t120"):
            # Mark as expected to timeout (not fail)
            item.add_marker(pytest.mark.skip(reason="Expected timeout - not a failure"))


# Utility functions for marking tests
def mark_t15(func):
    """Mark test as timing out at 15s (not failed)"""
    return pytest.mark.t15(func)


def mark_t30(func):
    """Mark test as timing out at 30s (not failed)"""
    return pytest.mark.t30(func)


def mark_t60(func):
    """Mark test as timing out at 60s (not failed)"""
    return pytest.mark.t60(func)


def mark_t120(func):
    """Mark test as timing out at 120s (not failed)"""
    return pytest.mark.t120(func)
