"""
PR 00 — Repository Structure Tests

Tests that verify the foundational repository structure is correct.
These tests ensure PR templates, trackers, and documentation are in place.
"""

import os
import glob
import pytest


@pytest.mark.pr00
def test_templates_exist():
    """Verify all 10 PR templates exist in .github/PULL_REQUEST_TEMPLATE/"""
    base = ".github/PULL_REQUEST_TEMPLATE"
    expected = [
        "01-system-readiness.md",
        "02-user-input-selection.md",
        "03-active-llms-preparation.md",
        "04-initial-round.md",
        "05-meta-round.md",
        "06-ultrai-synthesis.md",
        "07-addons-processing.md",
        "08-statistics.md",
        "09-final-delivery.md",
        "10-error-handling-fallbacks.md",
    ]
    for name in expected:
        path = os.path.join(base, name)
        assert os.path.isfile(path), f"Missing PR template: {path}"

@pytest.mark.pr00
def test_trackers_exist_and_nonempty():
    """Verify trackers/dependencies.md and trackers/names.md exist and have content"""
    assert os.path.isfile("trackers/dependencies.md"), "Missing trackers/dependencies.md"
    assert os.path.isfile("trackers/names.md"), "Missing trackers/names.md"
    assert os.path.getsize("trackers/dependencies.md") > 0, "dependencies.md is empty"
    assert os.path.getsize("trackers/names.md") > 0, "names.md is empty"

@pytest.mark.pr00
def test_index_links_match_files():
    """Verify pr_index.md references all PR template files"""
    assert os.path.isfile("pr_index.md"), "Missing pr_index.md"
    with open("pr_index.md", "r", encoding="utf-8") as f:
        idx = f.read()
    # verify each file mentioned in index actually exists
    for md in glob.glob(".github/PULL_REQUEST_TEMPLATE/*.md"):
        rel = md.replace("\\", "/")
        assert rel in idx, f"{rel} not referenced in pr_index.md"