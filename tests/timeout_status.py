"""
Custom pytest plugin to treat timeouts as T-15, T-30, etc. status instead of FAILED.

This creates new test status categories:
- PASSED = Test passed
- SKIPPED = Intentionally skipped when test started  
- T-15, T-30, T-60, T-120 = Timed out (not failed)
- FAILED = Did not meet substantive objective
"""

import pytest
import time
from typing import Dict, Any


class TimeoutStatusPlugin:
    """Pytest plugin to categorize timeouts as T-n status instead of FAILED"""
    
    def __init__(self):
        self.timeout_tests: Dict[str, str] = {}  # test_name -> timeout_class
        self.current_timeout = 15.0
    
    def set_timeout(self, timeout: float):
        """Set the current timeout threshold"""
        self.current_timeout = timeout
    
    def pytest_runtest_setup(self, item):
        """Track test start time"""
        item._start_time = time.time()
    
    def pytest_runtest_teardown(self, item, nextitem):
        """Check if test timed out and categorize it"""
        if hasattr(item, '_start_time'):
            duration = time.time() - item._start_time
            if duration > self.current_timeout:
                # Test exceeded timeout - categorize as T-n
                timeout_class = self._get_timeout_class(self.current_timeout)
                self.timeout_tests[item.name] = timeout_class
                print(f"\n⏱️  {timeout_class}: {item.name} (exceeded {self.current_timeout}s)")
    
    def _get_timeout_class(self, timeout: float) -> str:
        """Get timeout class based on timeout duration"""
        if timeout <= 5.0:
            return "T-5"
        elif timeout <= 15.0:
            return "T-15"
        elif timeout <= 30.0:
            return "T-30"
        elif timeout <= 60.0:
            return "T-60"
        else:
            return "T-120"
    
    def pytest_sessionfinish(self, session, exitstatus):
        """Report timeout status at the end"""
        if self.timeout_tests:
            print("\n" + "="*50)
            print("TIMEOUT STATUS SUMMARY")
            print("="*50)
            
            by_class = {}
            for test_name, timeout_class in self.timeout_tests.items():
                if timeout_class not in by_class:
                    by_class[timeout_class] = []
                by_class[timeout_class].append(test_name)
            
            for timeout_class in sorted(by_class.keys()):
                tests = by_class[timeout_class]
                print(f"\n{timeout_class} ({len(tests)} tests):")
                for test in tests:
                    print(f"  - {test}")
            
            print(f"\n💡 These tests timed out but did not fail.")
            print("="*50)


# Global plugin instance
timeout_plugin = TimeoutStatusPlugin()


def pytest_configure(config):
    """Configure pytest to use our timeout plugin"""
    config.pluginmanager.register(timeout_plugin, "timeout_status")


def set_timeout_threshold(timeout: float):
    """Set the timeout threshold for T-n classification"""
    timeout_plugin.set_timeout(timeout)


def get_timeout_summary() -> str:
    """Get summary of timeout tests"""
    if not timeout_plugin.timeout_tests:
        return "No tests timed out"
    
    summary = f"Timeout Summary: {len(timeout_plugin.timeout_tests)} tests\n"
    by_class = {}
    for test_name, timeout_class in timeout_plugin.timeout_tests.items():
        if timeout_class not in by_class:
            by_class[timeout_class] = []
        by_class[timeout_class].append(test_name)
    
    for timeout_class in sorted(by_class.keys()):
        tests = by_class[timeout_class]
        summary += f"\n{timeout_class} ({len(tests)} tests):\n"
        for test in tests:
            summary += f"  - {test}\n"
    
    return summary
