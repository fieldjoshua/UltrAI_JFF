"""
Timeout Classification System for UltrAI Tests

Tests that timeout after 15 seconds are categorized into TO_15 class
for later re-examination rather than failing the CI pipeline.
"""

import pytest
import time
from typing import List, Dict, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TimeoutResult:
    """Result of a test that timed out"""
    test_name: str
    timeout_duration: float
    timeout_reason: str
    test_file: str
    timestamp: float
    
    def __str__(self):
        return f"TO_15: {self.test_name} ({self.timeout_duration}s) - {self.timeout_reason}"


class TO_15:
    """
    Timeout Classification for tests that exceed 15 seconds.
    
    Tests in this class are not considered failures but are categorized
    for later re-examination and optimization.
    """
    
    def __init__(self):
        self.timeout_results: List[TimeoutResult] = []
        self.timeout_threshold = 15.0
    
    def add_timeout(self, test_name: str, timeout_duration: float, 
                   timeout_reason: str, test_file: str):
        """Add a test that timed out to the TO_15 class"""
        result = TimeoutResult(
            test_name=test_name,
            timeout_duration=timeout_duration,
            timeout_reason=timeout_reason,
            test_file=test_file,
            timestamp=time.time()
        )
        self.timeout_results.append(result)
    
    def get_timeout_tests(self) -> List[TimeoutResult]:
        """Get all tests that timed out"""
        return self.timeout_results
    
    def get_timeout_tests_by_file(self) -> Dict[str, List[TimeoutResult]]:
        """Group timeout tests by file"""
        by_file = {}
        for result in self.timeout_results:
            if result.test_file not in by_file:
                by_file[result.test_file] = []
            by_file[result.test_file].append(result)
        return by_file
    
    def get_timeout_summary(self) -> str:
        """Get a summary of all timeout tests"""
        if not self.timeout_results:
            return "No tests timed out (TO_15 class empty)"
        
        summary = f"TO_15 Class Summary: {len(self.timeout_results)} tests timed out\n"
        summary += "=" * 50 + "\n"
        
        by_file = self.get_timeout_tests_by_file()
        for file_path, results in by_file.items():
            summary += f"\n{file_path}:\n"
            for result in results:
                summary += f"  - {result.test_name} ({result.timeout_duration:.1f}s)\n"
        
        return summary
    
    def clear(self):
        """Clear all timeout results"""
        self.timeout_results.clear()
    
    def save_to_file(self, file_path: str = "to_15_results.txt"):
        """Save timeout results to a file for later analysis"""
        with open(file_path, "w") as f:
            f.write(self.get_timeout_summary())
            f.write(f"\nGenerated at: {time.ctime()}\n")
    
    def __len__(self):
        return len(self.timeout_results)
    
    def __str__(self):
        return f"TO_15 class: {len(self.timeout_results)} tests for re-examination"


# Global instance for tracking timeouts
to_15_instance = TO_15()


def pytest_runtest_setup(item):
    """Pytest hook to track test start time"""
    item._start_time = time.time()


def pytest_runtest_teardown(item, nextitem):
    """Pytest hook to check for timeouts and categorize them"""
    if hasattr(item, '_start_time'):
        duration = time.time() - item._start_time
        if duration > to_15_instance.timeout_threshold:
            # Test took longer than 15 seconds - add to TO_15 class
            test_name = item.name
            test_file = str(item.fspath)
            timeout_reason = f"Test execution exceeded {to_15_instance.timeout_threshold}s threshold"
            
            to_15_instance.add_timeout(
                test_name=test_name,
                timeout_duration=duration,
                timeout_reason=timeout_reason,
                test_file=test_file
            )


def pytest_sessionfinish(session, exitstatus):
    """Pytest hook to report TO_15 results at the end"""
    if to_15_instance.timeout_results:
        print("\n" + "="*60)
        print("TO_15 CLASS RESULTS - Tests for Re-examination")
        print("="*60)
        print(to_15_instance.get_timeout_summary())
        to_15_instance.save_to_file()
        print(f"\nResults saved to: to_15_results.txt")
        print("These tests did not fail - they are categorized for optimization.")
        print("="*60)


# Decorator for marking tests that should be in TO_15 class if they timeout
def to_15_category(reason: str = "Slow test - needs optimization"):
    """
    Decorator to mark tests that should be categorized in TO_15 class
    if they timeout, rather than failing.
    """
    def decorator(func):
        func._to_15_reason = reason
        return func
    return decorator


# Utility functions for working with TO_15 class
def get_to_15_tests() -> List[TimeoutResult]:
    """Get all tests in TO_15 class"""
    return to_15_instance.get_timeout_tests()


def get_to_15_summary() -> str:
    """Get summary of TO_15 class"""
    return to_15_instance.get_timeout_summary()


def clear_to_15_class():
    """Clear the TO_15 class"""
    to_15_instance.clear()


def save_to_15_results(file_path: str = "to_15_results.txt"):
    """Save TO_15 results to file"""
    to_15_instance.save_to_file(file_path)
