#!/usr/bin/env python3
"""
Test Status Dashboard

Shows test progression across all PR phases with color-coded pass/fail indicators.
Run with: python scripts/test_status.py or make test-summary
"""

import subprocess
import sys
import json
from typing import Dict, List, Tuple


# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def run_pytest_collect() -> Dict[str, List[str]]:
    """Collect all tests and group by PR marker"""
    try:
        result = subprocess.run(
            ['pytest', '--collect-only', '-q', '--color=no'],
            capture_output=True,
            text=True,
            check=True
        )

        # Parse output to extract test names
        tests_by_pr = {f'pr{i:02d}': [] for i in range(11)}  # pr00 to pr10

        for line in result.stdout.split('\n'):
            if '::test_' in line:
                test_name = line.strip()
                # Try to determine which PR this test belongs to based on file/markers
                if 'test_repo_structure.py' in test_name:
                    tests_by_pr['pr00'].append(test_name)
                elif 'test_system_readiness.py' in test_name:
                    tests_by_pr['pr01'].append(test_name)
                # Future PRs will be added here

        return tests_by_pr
    except subprocess.CalledProcessError as e:
        print(f"Error collecting tests: {e}")
        return {}


def run_pytest_for_marker(marker: str) -> Tuple[int, int, int]:
    """Run tests for a specific marker and return (passed, failed, skipped)"""
    try:
        result = subprocess.run(
            ['pytest', '-m', marker, '-v', '--tb=no', '--color=no', '-q'],
            capture_output=True,
            text=True
        )

        # Parse output to count results
        output = result.stdout + result.stderr
        passed = output.count(' PASSED')
        failed = output.count(' FAILED')
        skipped = output.count(' SKIPPED')

        return (passed, failed, skipped)
    except Exception as e:
        return (0, 0, 0)


def format_status(passed: int, failed: int, skipped: int, total: int) -> str:
    """Format test status with color coding"""
    if total == 0:
        return f"{YELLOW}0/0 ⏳{RESET}"

    if failed > 0:
        return f"{RED}{passed}/{total} ✗ ({failed} failed){RESET}"
    elif skipped > 0:
        return f"{YELLOW}{passed}/{total} ⊘ ({skipped} skipped){RESET}"
    elif passed == total:
        return f"{GREEN}{passed}/{total} ✓{RESET}"
    else:
        return f"{BLUE}{passed}/{total} ⋯{RESET}"


def main():
    """Main dashboard display"""
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}{'UltrAI Test Status Dashboard':^70}{RESET}")
    print(f"{BOLD}{'='*70}{RESET}\n")

    # PR phase definitions
    pr_phases = [
        ('pr00', 'Repository Structure'),
        ('pr01', 'System Readiness'),
        ('pr02', 'User Input Selection'),
        ('pr03', 'Active LLMs Preparation'),
        ('pr04', 'Initial Round'),
        ('pr05', 'Meta Round'),
        ('pr06', 'UltrAI Synthesis'),
        ('pr07', 'Add-ons Processing'),
        ('pr08', 'Statistics'),
        ('pr09', 'Final Delivery'),
        ('pr10', 'Error Handling & Fallbacks'),
    ]

    print(f"{'Phase':<8} {'Description':<35} {'Status':<25}")
    print(f"{'-'*70}")

    total_passed = 0
    total_failed = 0
    total_skipped = 0
    total_tests = 0

    for marker, description in pr_phases:
        passed, failed, skipped = run_pytest_for_marker(marker)
        total = passed + failed + skipped

        total_passed += passed
        total_failed += failed
        total_skipped += skipped
        total_tests += total

        status = format_status(passed, failed, skipped, total)
        print(f"{marker.upper():<8} {description:<35} {status}")

    print(f"{'-'*70}")

    # Overall summary
    print(f"\n{BOLD}Overall Summary:{RESET}")
    print(f"  Total Tests:   {total_tests}")
    print(f"  {GREEN}Passed:        {total_passed}{RESET}")
    if total_failed > 0:
        print(f"  {RED}Failed:        {total_failed}{RESET}")
    if total_skipped > 0:
        print(f"  {YELLOW}Skipped:       {total_skipped}{RESET}")

    completion_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"  Completion:    {completion_rate:.1f}%")

    print(f"\n{BOLD}{'='*70}{RESET}\n")

    # Exit with error code if there are failures
    sys.exit(1 if total_failed > 0 else 0)


if __name__ == '__main__':
    main()
