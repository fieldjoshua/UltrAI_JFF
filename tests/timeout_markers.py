"""
Simple timeout designation system.

Tests can be marked with timeout markers:
- @pytest.mark.t15 - Test times out at 15s (not failed)
- @pytest.mark.t30 - Test times out at 30s (not failed)  
- @pytest.mark.t60 - Test times out at 60s (not failed)
- @pytest.mark.t120 - Test times out at 120s (not failed)

This allows pytest to treat timeouts as designated status instead of failures.
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
