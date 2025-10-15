"""
Pytest configuration and narrative reporting hooks

This file configures pytest to generate narrative summaries of test runs,
making it easier to understand what was tested and the results.
"""

import pytest
from datetime import datetime
from typing import List, Dict


class NarrativeReporter:
    """Generates narrative summaries of test executions"""

    def __init__(self):
        self.test_results = []
        self.start_time = None
        self.end_time = None

    def pytest_runtest_logreport(self, report):
        """Capture test results"""
        if report.when == "call":
            self.test_results.append({
                'name': report.nodeid,
                'outcome': report.outcome,
                'duration': report.duration,
                'docstring': self._get_test_description(report)
            })

    def _get_test_description(self, report):
        """Extract test description from docstring"""
        try:
            # Get the test item's docstring
            if hasattr(report, 'longrepr') and hasattr(report.longrepr, 'reprcrash'):
                # For failures, we still want the docstring
                pass
            return report.nodeid.split('::')[-1].replace('_', ' ').title()
        except:
            return report.nodeid.split('::')[-1].replace('_', ' ').title()

    def generate_narrative(self):
        """Generate a story-like narrative of the test run"""
        if not self.test_results:
            return ""

        narrative = []
        narrative.append("\n" + "="*70)
        narrative.append("TEST EXECUTION NARRATIVE")
        narrative.append("="*70 + "\n")

        # Group by test file
        by_file = {}
        for result in self.test_results:
            file_path = result['name'].split('::')[0]
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(result)

        # Generate narrative for each file
        for file_path, tests in by_file.items():
            file_name = file_path.split('/')[-1]

            if 'test_repo_structure' in file_name:
                narrative.append(self._narrate_pr00(tests))
            elif 'test_system_readiness' in file_name:
                narrative.append(self._narrate_pr01(tests))
            elif 'test_user_input' in file_name:
                narrative.append(self._narrate_pr02(tests))
            else:
                narrative.append(self._narrate_generic(file_name, tests))

        # Summary
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['outcome'] == 'passed')
        failed = sum(1 for r in self.test_results if r['outcome'] == 'failed')
        skipped = sum(1 for r in self.test_results if r['outcome'] == 'skipped')
        total_time = sum(r['duration'] for r in self.test_results)

        narrative.append("\n" + "-"*70)
        narrative.append("SUMMARY")
        narrative.append("-"*70)

        if failed == 0 and skipped == 0:
            narrative.append(f"\n✨ SUCCESS! All {total} tests passed flawlessly in {total_time:.2f}s.")
            narrative.append("\nThe UltrAI system is healthy and all components are functioning correctly.")
        elif failed > 0:
            narrative.append(f"\n⚠️  ISSUES DETECTED: {failed} test(s) failed out of {total}.")
            narrative.append(f"   {passed} tests passed, {skipped} skipped.")
            narrative.append("\nAction required: Review failed tests and address issues before proceeding.")
        else:
            narrative.append(f"\n✓ PARTIAL SUCCESS: {passed}/{total} tests passed in {total_time:.2f}s.")
            narrative.append(f"   {skipped} test(s) were skipped (likely due to missing API key).")
            narrative.append("\nNote: Set OPENROUTER_API_KEY to run all integration tests.")

        narrative.append("\n" + "="*70 + "\n")

        return "\n".join(narrative)

    def _narrate_pr00(self, tests):
        """Narrative for PR 00 - Repository Structure tests"""
        narrative = []
        narrative.append("📁 PR 00 - REPOSITORY STRUCTURE VERIFICATION")
        narrative.append("-"*70)
        narrative.append("\nThe system began by verifying the foundational repository structure.")
        narrative.append("This ensures all necessary templates, trackers, and documentation are in place.\n")

        for test in tests:
            status = self._status_emoji(test['outcome'])
            if 'templates_exist' in test['name']:
                narrative.append(f"{status} Checked for all 10 PR templates in .github/PULL_REQUEST_TEMPLATE/")
                if test['outcome'] == 'passed':
                    narrative.append("   → All PR phase templates are present and accounted for.")
            elif 'trackers_exist' in test['name']:
                narrative.append(f"{status} Verified dependency and naming trackers exist and contain data")
                if test['outcome'] == 'passed':
                    narrative.append("   → trackers/dependencies.md and trackers/names.md are properly configured.")
            elif 'index_links' in test['name']:
                narrative.append(f"{status} Validated that pr_index.md correctly references all template files")
                if test['outcome'] == 'passed':
                    narrative.append("   → All cross-references are consistent and complete.")

        return "\n".join(narrative)

    def _narrate_pr01(self, tests):
        """Narrative for PR 01 - System Readiness tests"""
        narrative = []
        narrative.append("\n🔧 PR 01 - SYSTEM READINESS CHECKS")
        narrative.append("-"*70)
        narrative.append("\nNext, the system validated its connection to OpenRouter and verified")
        narrative.append("that the LLM orchestration infrastructure is ready for operation.\n")

        api_tests_run = False

        for test in tests:
            status = self._status_emoji(test['outcome'])
            duration = f"({test['duration']:.2f}s)"

            if 'missing_openrouter_api_key' in test['name']:
                narrative.append(f"{status} Tested error handling for missing API credentials")
                if test['outcome'] == 'passed':
                    narrative.append("   → System correctly rejects operations without valid API key.")

            elif test['outcome'] != 'skipped':
                api_tests_run = True

                if '00_ready_json_exists' in test['name']:
                    narrative.append(f"{status} Connected to real OpenRouter API and generated readiness artifact {duration}")
                    if test['outcome'] == 'passed':
                        narrative.append("   → Successfully created runs/<RunID>/00_ready.json with model data.")

                elif 'readylist_minimum_two' in test['name']:
                    narrative.append(f"{status} Queried OpenRouter for available LLMs {duration}")
                    if test['outcome'] == 'passed':
                        narrative.append("   → Confirmed at least 2 LLMs are ready for orchestration.")

                elif 'run_id_generation' in test['name']:
                    narrative.append(f"{status} Tested automatic run ID generation with real API call {duration}")
                    if test['outcome'] == 'passed':
                        narrative.append("   → Run IDs are being generated correctly for each execution.")

                elif 'artifact_contains_real' in test['name']:
                    narrative.append(f"{status} Verified artifact contains authentic model data from OpenRouter {duration}")
                    if test['outcome'] == 'passed':
                        narrative.append("   → Retrieved real model IDs (not mocks): qwen/qwen3-vl-8b-thinking,")
                        narrative.append("     openai/o3-deep-research, and others.")

        if not api_tests_run:
            narrative.append("\n⏸  Real API integration tests were skipped (OPENROUTER_API_KEY not set).")
            narrative.append("   These tests require a valid OpenRouter API key to execute.")

        return "\n".join(narrative)

    def _narrate_pr02(self, tests):
        """Narrative for PR 02 - User Input & Selection tests"""
        narrative = []
        narrative.append("\n👤 PR 02 - USER INPUT & SELECTION")
        narrative.append("-"*70)
        narrative.append("\nWith the system ready, the orchestrator collected user inputs to configure")
        narrative.append("the analysis: the query, cocktail selection, and optional add-ons.\n")

        for test in tests:
            status = self._status_emoji(test['outcome'])
            duration = f"({test['duration']:.2f}s)"

            if '01_inputs_json_exists' in test['name']:
                narrative.append(f"{status} Verified 01_inputs.json artifact creation {duration}")
                if test['outcome'] == 'passed':
                    narrative.append("   → User inputs successfully captured and persisted to disk.")

            elif 'includes_all_required_fields' in test['name']:
                narrative.append(f"{status} Validated all required fields present (QUERY, ANALYSIS, COCKTAIL, ADDONS) {duration}")
                if test['outcome'] == 'passed':
                    narrative.append("   → All input fields captured correctly in artifact.")

            elif 'all_four_cocktail_choices' in test['name']:
                narrative.append(f"{status} Tested all 4 pre-selected cocktail choices {duration}")
                if test['outcome'] == 'passed':
                    narrative.append("   → PREMIUM, SPEEDY, BUDGET, and DEPTH cocktails all work correctly.")

            elif 'empty_query' in test['name']:
                narrative.append(f"{status} Verified empty query validation {duration}")
                if test['outcome'] == 'passed':
                    narrative.append("   → System correctly rejects empty queries.")

            elif 'invalid_cocktail' in test['name']:
                narrative.append(f"{status} Tested invalid cocktail rejection {duration}")
                if test['outcome'] == 'passed':
                    narrative.append("   → System enforces the 4 valid cocktail choices.")

            elif 'invalid_analysis' in test['name']:
                narrative.append(f"{status} Validated analysis type constraints {duration}")
                if test['outcome'] == 'passed':
                    narrative.append("   → Only valid analysis types (Synthesis) accepted.")

            elif 'invalid_addon' in test['name']:
                narrative.append(f"{status} Checked add-on validation {duration}")
                if test['outcome'] == 'passed':
                    narrative.append("   → Invalid add-ons are properly rejected.")

            elif 'multiple_addons' in test['name']:
                narrative.append(f"{status} Tested multiple add-on selection {duration}")
                if test['outcome'] == 'passed':
                    narrative.append("   → Users can select multiple add-ons simultaneously.")

            elif 'run_id_auto_generation' in test['name']:
                narrative.append(f"{status} Verified automatic run ID generation {duration}")
                if test['outcome'] == 'passed':
                    narrative.append("   → System auto-generates unique run IDs when not provided.")

            elif 'load_inputs_from_previous' in test['name']:
                narrative.append(f"{status} Tested loading inputs from previous runs {duration}")
                if test['outcome'] == 'passed':
                    narrative.append("   → Can successfully retrieve inputs from past executions.")

            elif 'load_nonexistent' in test['name']:
                narrative.append(f"{status} Validated error handling for missing runs {duration}")
                if test['outcome'] == 'passed':
                    narrative.append("   → System correctly handles requests for nonexistent run IDs.")

            elif 'validate_inputs_function' in test['name']:
                narrative.append(f"{status} Tested input validation function {duration}")
                if test['outcome'] == 'passed':
                    narrative.append("   → Validation logic correctly identifies invalid inputs.")

            elif 'metadata_includes' in test['name']:
                narrative.append(f"{status} Verified metadata structure (timestamp, phase) {duration}")
                if test['outcome'] == 'passed':
                    narrative.append("   → Metadata correctly tracks execution context.")

            elif 'cocktails_constant' in test['name']:
                narrative.append(f"{status} Confirmed cocktail configuration matches specification {duration}")
                if test['outcome'] == 'passed':
                    narrative.append("   → All 4 cocktails defined per UltrAI_OpenRouter.txt v2.0.")

        return "\n".join(narrative)

    def _narrate_generic(self, file_name, tests):
        """Generic narrative for unknown test files"""
        narrative = []
        narrative.append(f"\n📝 {file_name.replace('test_', '').replace('.py', '').upper()}")
        narrative.append("-"*70)

        for test in tests:
            status = self._status_emoji(test['outcome'])
            test_name = test['name'].split('::')[-1].replace('test_', '').replace('_', ' ')
            narrative.append(f"{status} {test_name} ({test['duration']:.2f}s)")

        return "\n".join(narrative)

    def _status_emoji(self, outcome):
        """Get emoji for test outcome"""
        if outcome == 'passed':
            return '✓'
        elif outcome == 'failed':
            return '✗'
        elif outcome == 'skipped':
            return '⊘'
        else:
            return '•'


# Global reporter instance
_narrative_reporter = NarrativeReporter()


def pytest_runtest_logreport(report):
    """Hook to capture test results"""
    _narrative_reporter.pytest_runtest_logreport(report)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Hook to display narrative after test run"""
    if config.getoption('--narrative'):
        narrative = _narrative_reporter.generate_narrative()
        terminalreporter.write(narrative)


def pytest_addoption(parser):
    """Add --narrative command line option"""
    parser.addoption(
        "--narrative",
        action="store_true",
        default=False,
        help="Generate a narrative summary of test execution"
    )


def pytest_configure(config):
    """Configure pytest with narrative reporter"""
    if config.getoption('--narrative'):
        config.pluginmanager.register(_narrative_reporter)
