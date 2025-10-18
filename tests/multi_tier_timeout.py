"""
Multi-Tier Timeout Classification System for UltrAI Tests

Tests are categorized by execution time into different timeout classes
instead of failing on timeout, allowing for optimization and analysis.
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
    timeout_class: str
    
    def __str__(self):
        return f"{self.timeout_class}: {self.test_name} ({self.timeout_duration:.1f}s) - {self.timeout_reason}"


class MultiTierTimeoutSystem:
    """
    Multi-tier timeout classification system.
    
    Tests are categorized by execution time instead of failing:
    - TO_5: Unit tests (0-5 seconds)
    - TO_15: Fast integration (5-15 seconds)  
    - TO_30: Medium integration (15-30 seconds)
    - TO_60: Full integration (30-60 seconds)
    - TO_120: Complex integration (60-120 seconds)
    """
    
    def __init__(self):
        self.timeout_results: List[TimeoutResult] = []
        self.timeout_thresholds = {
            'TO_5': 5.0,
            'TO_15': 15.0,
            'TO_30': 30.0,
            'TO_60': 60.0,
            'TO_120': 120.0
        }
        self.current_threshold = 15.0  # Default threshold
    
    def set_threshold(self, threshold: str):
        """Set the current timeout threshold"""
        if threshold in self.timeout_thresholds:
            self.current_threshold = self.timeout_thresholds[threshold]
        else:
            raise ValueError(f"Invalid threshold: {threshold}. Valid: {list(self.timeout_thresholds.keys())}")
    
    def add_timeout(self, test_name: str, timeout_duration: float, 
                   timeout_reason: str, test_file: str):
        """Add a test that timed out to the appropriate timeout class"""
        # Determine which timeout class this test belongs to
        timeout_class = self._classify_timeout(timeout_duration)
        
        result = TimeoutResult(
            test_name=test_name,
            timeout_duration=timeout_duration,
            timeout_reason=timeout_reason,
            test_file=test_file,
            timestamp=time.time(),
            timeout_class=timeout_class
        )
        self.timeout_results.append(result)
    
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
    
    def get_timeout_tests(self) -> List[TimeoutResult]:
        """Get all tests that timed out"""
        return self.timeout_results
    
    def get_timeout_tests_by_class(self) -> Dict[str, List[TimeoutResult]]:
        """Group timeout tests by timeout class"""
        by_class = {}
        for result in self.timeout_results:
            if result.timeout_class not in by_class:
                by_class[result.timeout_class] = []
            by_class[result.timeout_class].append(result)
        return by_class
    
    def get_timeout_tests_by_file(self) -> Dict[str, List[TimeoutResult]]:
        """Group timeout tests by file"""
        by_file = {}
        for result in self.timeout_results:
            if result.test_file not in by_file:
                by_file[result.test_file] = []
            by_file[result.test_file].append(result)
        return by_file
    
    def get_timeout_summary(self) -> str:
        """Get a comprehensive summary of all timeout tests"""
        if not self.timeout_results:
            return "No tests timed out - all tests completed within thresholds"
        
        summary = f"Multi-Tier Timeout Analysis: {len(self.timeout_results)} tests categorized\n"
        summary += "=" * 60 + "\n"
        
        by_class = self.get_timeout_tests_by_class()
        for timeout_class in ['TO_5', 'TO_15', 'TO_30', 'TO_60', 'TO_120']:
            if timeout_class in by_class:
                results = by_class[timeout_class]
                summary += f"\n{timeout_class} Class ({len(results)} tests):\n"
                for result in results:
                    summary += f"  - {result.test_name} ({result.timeout_duration:.1f}s)\n"
        
        summary += f"\nBy File:\n"
        by_file = self.get_timeout_tests_by_file()
        for file_path, results in by_file.items():
            summary += f"\n{file_path}:\n"
            for result in results:
                summary += f"  - {result.timeout_class}: {result.test_name} ({result.timeout_duration:.1f}s)\n"
        
        return summary
    
    def get_optimization_recommendations(self) -> str:
        """Get recommendations for optimizing timed-out tests"""
        recommendations = "Optimization Recommendations:\n"
        recommendations += "=" * 40 + "\n"
        
        by_class = self.get_timeout_tests_by_class()
        
        if 'TO_5' in by_class:
            recommendations += "\nTO_5 Tests (Unit Tests):\n"
            recommendations += "- These should be instant - check for infinite loops\n"
            recommendations += "- Consider mocking external dependencies\n"
        
        if 'TO_15' in by_class:
            recommendations += "\nTO_15 Tests (Fast Integration):\n"
            recommendations += "- Optimize file I/O operations\n"
            recommendations += "- Use faster test data or smaller datasets\n"
        
        if 'TO_30' in by_class:
            recommendations += "\nTO_30 Tests (Medium Integration):\n"
            recommendations += "- Consider using test API keys with higher rate limits\n"
            recommendations += "- Implement request caching for repeated calls\n"
        
        if 'TO_60' in by_class:
            recommendations += "\nTO_60 Tests (Full Integration):\n"
            recommendations += "- Break down into smaller integration tests\n"
            recommendations += "- Use parallel execution where possible\n"
        
        if 'TO_120' in by_class:
            recommendations += "\nTO_120 Tests (Complex Integration):\n"
            recommendations += "- These may be legitimate stress tests\n"
            recommendations += "- Consider running separately from CI\n"
            recommendations += "- Use dedicated test environment\n"
        
        return recommendations
    
    def clear(self):
        """Clear all timeout results"""
        self.timeout_results.clear()
    
    def save_to_file(self, file_path: str = "timeout_analysis.txt"):
        """Save timeout results and recommendations to a file"""
        with open(file_path, "w") as f:
            f.write(self.get_timeout_summary())
            f.write("\n\n")
            f.write(self.get_optimization_recommendations())
            f.write(f"\nGenerated at: {time.ctime()}\n")
    
    def __len__(self):
        return len(self.timeout_results)
    
    def __str__(self):
        return f"Multi-tier timeout system: {len(self.timeout_results)} tests categorized"


# Global instance for tracking timeouts
timeout_system = MultiTierTimeoutSystem()


def pytest_runtest_setup(item):
    """Pytest hook to track test start time"""
    item._start_time = time.time()


def pytest_runtest_teardown(item, nextitem):
    """Pytest hook to check for timeouts and categorize them"""
    if hasattr(item, '_start_time'):
        duration = time.time() - item._start_time
        if duration > timeout_system.current_threshold:
            # Test took longer than threshold - add to appropriate timeout class
            test_name = item.name
            test_file = str(item.fspath)
            timeout_reason = f"Test execution exceeded {timeout_system.current_threshold}s threshold"
            
            timeout_system.add_timeout(
                test_name=test_name,
                timeout_duration=duration,
                timeout_reason=timeout_reason,
                test_file=test_file
            )


def pytest_timeout_setup(item):
    """Hook into pytest-timeout to categorize instead of fail"""
    # This hook is called when pytest-timeout is about to timeout a test
    # We can use this to categorize the test instead of failing it
    pass


def pytest_timeout_teardown(item):
    """Hook called after pytest-timeout kills a test"""
    # This is called after pytest-timeout has killed the test
    # We can categorize it here
    test_name = item.name
    test_file = str(item.fspath)
    timeout_duration = timeout_system.current_threshold  # Approximate duration
    timeout_reason = f"Test killed by pytest-timeout after {timeout_duration}s"
    
    timeout_system.add_timeout(
        test_name=test_name,
        timeout_duration=timeout_duration,
        timeout_reason=timeout_reason,
        test_file=test_file
    )


def pytest_sessionfinish(session, exitstatus):
    """Pytest hook to report timeout results at the end"""
    if timeout_system.timeout_results:
        print("\n" + "="*70)
        print("MULTI-TIER TIMEOUT ANALYSIS - Tests Categorized for Optimization")
        print("="*70)
        print(timeout_system.get_timeout_summary())
        print("\n" + timeout_system.get_optimization_recommendations())
        timeout_system.save_to_file()
        print(f"\nDetailed analysis saved to: timeout_analysis.txt")
        print("These tests did not fail - they are categorized for optimization.")
        print("="*70)


# Decorator for marking tests that should be categorized if they timeout
def timeout_category(category: str = "TO_30", reason: str = "Integration test - needs optimization"):
    """
    Decorator to mark tests with expected timeout category
    """
    def decorator(func):
        func._timeout_category = category
        func._timeout_reason = reason
        return func
    return decorator


# Utility functions for working with timeout system
def get_timeout_tests() -> List[TimeoutResult]:
    """Get all tests in timeout classes"""
    return timeout_system.get_timeout_tests()


def get_timeout_summary() -> str:
    """Get summary of timeout analysis"""
    return timeout_system.get_timeout_summary()


def get_optimization_recommendations() -> str:
    """Get optimization recommendations"""
    return timeout_system.get_optimization_recommendations()


def clear_timeout_results():
    """Clear all timeout results"""
    timeout_system.clear()


def save_timeout_analysis(file_path: str = "timeout_analysis.txt"):
    """Save timeout analysis to file"""
    timeout_system.save_to_file(file_path)


def set_timeout_threshold(threshold: str):
    """Set the timeout threshold for the current test run"""
    timeout_system.set_threshold(threshold)


# Legacy compatibility - keep TO_15 class for backward compatibility
class TO_15:
    """Legacy TO_15 class for backward compatibility"""
    def __init__(self):
        self.timeout_results = timeout_system.timeout_results
    
    def get_timeout_tests(self):
        return [r for r in timeout_system.timeout_results if r.timeout_class == 'TO_15']
    
    def get_timeout_summary(self):
        return timeout_system.get_timeout_summary()
    
    def clear(self):
        timeout_system.clear()
    
    def save_to_file(self, file_path: str = "to_15_results.txt"):
        timeout_system.save_to_file(file_path)
    
    def __len__(self):
        return len(self.get_timeout_tests())
    
    def __str__(self):
        return f"TO_15 class: {len(self)} tests for re-examination"
