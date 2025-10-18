"""
Test timeout display functionality

These tests verify that tests marked with timeout markers show
"TO-15", "TO-30", etc. instead of "FAILED" when they timeout.
"""

import pytest
import time


@pytest.mark.t15
@pytest.mark.timeout(15)
def test_intentional_timeout_15s():
    """This test intentionally times out at 15 seconds"""
    time.sleep(20)  # Sleep longer than timeout
    assert True  # Never reached


@pytest.mark.t30
@pytest.mark.timeout(30)
def test_intentional_timeout_30s():
    """This test intentionally times out at 30 seconds"""
    time.sleep(35)  # Sleep longer than timeout
    assert True  # Never reached


@pytest.mark.t60
@pytest.mark.timeout(60)
def test_intentional_timeout_60s():
    """This test intentionally times out at 60 seconds"""
    time.sleep(65)  # Sleep longer than timeout
    assert True  # Never reached


def test_normal_pass():
    """This test should pass normally"""
    assert True


def test_normal_fail():
    """This test should fail normally (not timeout)"""
    assert False, "This is a normal failure, not a timeout"
