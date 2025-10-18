"""
Test Status Diagnostic System

Shows exactly WHY each test didn't pass:
- PASSED = Test met its objective
- SKIPPED = Intentionally skipped when test started
- T-15, T-30, T-60, T-120 = Timed out (diagnostic info)
- FAILED = Did not meet substantive objective (diagnostic info)
"""

import pytest
import time
from typing import Dict, List


class TestDiagnostics:
    """Track why tests didn't pass"""
    
    def __init__(self):
        self.results: Dict[str, str] = {}
        self.timeout_threshold = 30.0
    
    def set_timeout(self, timeout: float):
        """Set timeout threshold"""
        self.timeout_threshold = timeout
    
    def record_timeout(self, test_name: str, duration: float):
        """Record a timeout with diagnostic info"""
        timeout_class = self._get_timeout_class(duration)
        self.results[test_name] = f"{timeout_class} (timed out after {duration:.1f}s)"
    
    def record_failure(self, test_name: str, reason: str):
        """Record a failure with diagnostic info"""
        self.results[test_name] = f"FAILED ({reason})"
    
    def _get_timeout_class(self, duration: float) -> str:
        """Get timeout class"""
        if duration <= 15.0:
            return "T-15"
        elif duration <= 30.0:
            return "T-30"
        elif duration <= 60.0:
            return "T-60"
        else:
            return "T-120"
    
    def get_diagnostics(self) -> str:
        """Get diagnostic summary"""
        if not self.results:
            return "✅ All tests passed or were intentionally skipped"
        
        summary = f"🔍 Test Diagnostics: {len(self.results)} tests didn't pass\n"
        summary += "=" * 60 + "\n"
        
        by_type = {}
        for test_name, reason in self.results.items():
            if reason.startswith("T-"):
                timeout_class = reason.split()[0]
                if timeout_class not in by_type:
                    by_type[timeout_class] = []
                by_type[timeout_class].append(f"{test_name}: {reason}")
            else:
                if "FAILED" not in by_type:
                    by_type["FAILED"] = []
                by_type["FAILED"].append(f"{test_name}: {reason}")
        
        for status_type in ["T-15", "T-30", "T-60", "T-120", "FAILED"]:
            if status_type in by_type:
                tests = by_type[status_type]
                summary += f"\n{status_type} ({len(tests)} tests):\n"
                for test in tests:
                    summary += f"  - {test}\n"
        
        return summary


# Global diagnostics instance
diagnostics = TestDiagnostics()


def pytest_runtest_setup(item):
    """Track test start"""
    item._start_time = time.time()


def pytest_runtest_teardown(item, nextitem):
    """Record why test didn't pass"""
    if hasattr(item, '_start_time'):
        duration = time.time() - item._start_time
        if duration > diagnostics.timeout_threshold:
            diagnostics.record_timeout(item.name, duration)


def pytest_runtest_logreport(report):
    """Record test failures with reasons"""
    if report.failed and not report.skipped:
        # Extract failure reason from report
        reason = "Unknown error"
        if hasattr(report, 'longrepr') and report.longrepr:
            reason = str(report.longrepr).split('\n')[0][:100]
        diagnostics.record_failure(report.nodeid, reason)


def pytest_sessionfinish(session, exitstatus):
    """Show diagnostic summary"""
    print("\n" + diagnostics.get_diagnostics())


def set_timeout_threshold(timeout: float):
    """Set timeout threshold"""
    diagnostics.set_timeout(timeout)


def get_diagnostics() -> str:
    """Get diagnostic summary"""
    return diagnostics.get_diagnostics()
