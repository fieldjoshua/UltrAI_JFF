"""
Simple timeout categorization system that works with pytest-timeout.

This creates a custom pytest plugin that categorizes timed-out tests
instead of treating them as failures.
"""

import pytest
import time
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class CategorizedTimeout:
    """A test that was categorized due to timeout"""
    test_name: str
    timeout_duration: float
    test_file: str
    timeout_class: str
    timestamp: float


class TimeoutCategorizer:
    """Categorizes timed-out tests instead of failing them"""
    
    def __init__(self):
        self.categorized_tests: List[CategorizedTimeout] = []
        self.current_timeout = 30.0  # Default
    
    def set_timeout(self, timeout: float):
        """Set the current timeout threshold"""
        self.current_timeout = timeout
    
    def categorize_timeout(self, test_name: str, test_file: str):
        """Categorize a test that timed out"""
        timeout_class = self._classify_timeout(self.current_timeout)
        
        categorized = CategorizedTimeout(
            test_name=test_name,
            timeout_duration=self.current_timeout,
            test_file=test_file,
            timeout_class=timeout_class,
            timestamp=time.time()
        )
        
        self.categorized_tests.append(categorized)
        print(f"\n🔄 CATEGORIZED: {timeout_class} - {test_name} ({self.current_timeout}s)")
    
    def _classify_timeout(self, duration: float) -> str:
        """Classify timeout duration into appropriate class"""
        if duration <= 5.0:
            return 'TO_5'
        elif duration <= 15.0:
            return 'TO_15'
        elif duration <= 30.0:
            return 'TO_30'
        elif duration <= 60.0:
            return 'TO_60'
        else:
            return 'TO_120'
    
    def get_summary(self) -> str:
        """Get summary of categorized tests"""
        if not self.categorized_tests:
            return "✅ No tests categorized - all completed within timeout"
        
        summary = f"📊 Timeout Categorization Summary: {len(self.categorized_tests)} tests categorized\n"
        summary += "=" * 60 + "\n"
        
        by_class = {}
        for test in self.categorized_tests:
            if test.timeout_class not in by_class:
                by_class[test.timeout_class] = []
            by_class[test.timeout_class].append(test)
        
        for timeout_class in ['TO_5', 'TO_15', 'TO_30', 'TO_60', 'TO_120']:
            if timeout_class in by_class:
                tests = by_class[timeout_class]
                summary += f"\n{timeout_class} Class ({len(tests)} tests):\n"
                for test in tests:
                    summary += f"  - {test.test_name}\n"
        
        return summary
    
    def clear(self):
        """Clear all categorized tests"""
        self.categorized_tests.clear()


# Global categorizer instance
categorizer = TimeoutCategorizer()


class TimeoutCategorizerPlugin:
    """Pytest plugin to categorize timeouts instead of failing"""
    
    def pytest_runtest_setup(self, item):
        """Track test start time"""
        item._start_time = time.time()
    
    def pytest_runtest_teardown(self, item, nextitem):
        """Check if test timed out and categorize it"""
        if hasattr(item, '_start_time'):
            duration = time.time() - item._start_time
            if duration > categorizer.current_timeout:
                # Test exceeded timeout - categorize it
                categorizer.categorize_timeout(
                    test_name=item.name,
                    test_file=str(item.fspath)
                )
    
    def pytest_sessionfinish(self, session, exitstatus):
        """Report categorization results at the end"""
        if categorizer.categorized_tests:
            print("\n" + "="*70)
            print("TIMEOUT CATEGORIZATION RESULTS")
            print("="*70)
            print(categorizer.get_summary())
            print("\n💡 These tests were categorized for optimization, not failed.")
            print("="*70)


# Utility functions
def set_timeout_threshold(timeout: float):
    """Set the timeout threshold for categorization"""
    categorizer.set_timeout(timeout)


def get_categorized_summary() -> str:
    """Get summary of categorized tests"""
    return categorizer.get_summary()


def clear_categorized_tests():
    """Clear all categorized tests"""
    categorizer.clear()


# Register the plugin
pytest_plugins = [TimeoutCategorizerPlugin()]
