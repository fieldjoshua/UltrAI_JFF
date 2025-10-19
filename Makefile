.PHONY: venv install test test-narrative test-verbose test-summary list-tests test-pr00 test-pr01 test-pr02 test-pr03 test-pr04 test-pr05 test-pr06 test-pr07 test-pr08 test-pr09 test-pr10 test-failed test-real-api test-integration test-report test-watch timings run-api deploy-render ci test-to-5 test-to-15 test-to-30 test-to-60 test-to-120 test-timeout-analysis test-UAI test-UAILite

venv:
	python3 -m venv .venv

install: venv
	. .venv/bin/activate && pip install -U pip && pip install -r requirements.txt

# Quick test with summary
test:
	@echo "Running all tests..."
	. .venv/bin/activate && pytest

# Run tests with narrative summary
test-narrative:
	@echo "Running tests with narrative summary..."
	. .venv/bin/activate && pytest --narrative

# Detailed verbose output
test-verbose:
	@echo "Running tests with detailed output..."
	. .venv/bin/activate && pytest -vv

# Clean summary by PR phase
test-summary:
	@echo "Test Summary by PR Phase:"
	@echo "=========================="
	. .venv/bin/activate && python scripts/test_status.py

# List all tests with descriptions
list-tests:
	@echo "Listing all tests with descriptions..."
	@echo ""
	. .venv/bin/activate && pytest --collect-only -v

# Run tests for specific PR phases
test-pr00:
	@echo "Running PR 00 (Repository Structure) tests..."
	. .venv/bin/activate && pytest -m pr00 -v

test-pr01:
	@echo "Running PR 01 (System Readiness) tests..."
	. .venv/bin/activate && pytest -m pr01 -v

test-pr02:
	@echo "Running PR 02 (User Input Selection) tests..."
	. .venv/bin/activate && pytest -m pr02 -v

test-pr03:
	@echo "Running PR 03 (Active LLMs Preparation) tests..."
	. .venv/bin/activate && pytest -m pr03 -v

test-pr04:
	@echo "Running PR 04 (Initial Round) tests..."
	. .venv/bin/activate && pytest -m pr04 -v

test-pr05:
	@echo "Running PR 05 (Meta Round) tests..."
	. .venv/bin/activate && pytest -m pr05 -v

test-pr06:
	@echo "Running PR 06 (UltrAI Synthesis) tests..."
	. .venv/bin/activate && pytest -m pr06 -v

test-pr07:
	@echo "Running PR 07 (Add-ons Processing) tests..."
	. .venv/bin/activate && pytest -m pr07 -v

test-pr08:
	@echo "Running PR 08 (Statistics) tests..."
	. .venv/bin/activate && pytest -m pr08 -v

test-pr09:
	@echo "Running PR 09 (Final Delivery) tests..."
	. .venv/bin/activate && pytest -m pr09 -v

test-pr10:
	@echo "Running PR 10 (Error Handling) tests..."
	. .venv/bin/activate && pytest -m pr10 -v

# Show only failed tests
test-failed:
	@echo "Running tests and showing only failures..."
	. .venv/bin/activate && pytest --tb=line --maxfail=1 -x

# Run only tests that require real API
test-real-api:
	@echo "Running tests that require real OpenRouter API..."
	. .venv/bin/activate && pytest -m real_api -v

# Run integration tests (verify all features work together)
test-integration:
	@echo "Running integration tests..."
	. .venv/bin/activate && pytest -m integration -v

# Generate HTML test report
test-report:
	@echo "Generating HTML test report..."
	. .venv/bin/activate && pytest --html=test-report.html --self-contained-html
	@echo "Report generated: test-report.html"

# Watch for changes and re-run tests (requires pytest-watch)
test-watch:
	@echo "Watching for changes and running tests..."
	. .venv/bin/activate && ptw --runner "pytest -v"

# Run the UltrAI CLI
run:
	@echo "Starting UltrAI CLI..."
	. .venv/bin/activate && python -m ultrai.cli

# Start local API server (FastAPI)
run-api:
	@echo "Starting UltrAI API on http://127.0.0.1:8000 ..."
	. .venv/bin/activate && uvicorn ultrai.api:app --host 0.0.0.0 --port 8000

ci: install test
	@echo "OK"

# Timeout status testing (T-15, T-30, etc. instead of FAILED)
test-t15:
	@echo "Running tests with T-15 timeout status..."
	. .venv/bin/activate && python -c "from tests.timeout_status import set_timeout_threshold; set_timeout_threshold(15.0)" && pytest --timeout=15 -v

test-t30:
	@echo "Running tests with T-30 timeout status..."
	. .venv/bin/activate && python -c "from tests.timeout_status import set_timeout_threshold; set_timeout_threshold(30.0)" && pytest --timeout=30 -v

test-t60:
	@echo "Running tests with T-60 timeout status..."
	. .venv/bin/activate && python -c "from tests.timeout_status import set_timeout_threshold; set_timeout_threshold(60.0)" && pytest --timeout=60 -v

test-t120:
	@echo "Running tests with T-120 timeout status..."
	. .venv/bin/activate && python -c "from tests.timeout_status import set_timeout_threshold; set_timeout_threshold(120.0)" && pytest --timeout=120 -v

# Show timeout status summary
test-timeout-status:
	@echo "Timeout Status Summary:"
	. .venv/bin/activate && python -c "from tests.timeout_status import get_timeout_summary; print(get_timeout_summary())"

# Benchmark cocktail timings and export CSV
timings:
	@echo "Running cocktail timings benchmark..."
	. .venv/bin/activate && python scripts/cocktail_timings.py

# Deploy to Render using render.yaml (requires render CLI or GitHub integration)
deploy-render:
	@echo "Installing dependencies..."
	. .venv/bin/activate && pip install -U pip && pip install -r requirements.txt
	@echo "Ensure your repository is connected to Render with render.yaml in root."
	@echo "Commit and push to trigger an autodeploy on Render."
	@echo "After deploy, set ULTRAI_API_BASE to your Render URL and run: make run-api (local) or tests against the live URL."

# Production health check - comprehensive (3 tests, ~4 minutes)
test-UAI:
	@echo "Running UltrAI production health check (3 tests)..."
	. .venv/bin/activate && pytest \
		tests/test_render_deployment.py::test_step_00_backend_health \
		tests/test_render_deployment.py::test_step_01_frontend_loads \
		tests/test_render_deployment.py::test_step_05_r3_synthesis_completes \
		-v

# Production health check - minimal (1 test, ~3 minutes)
test-UAILite:
	@echo "Running UltrAI Lite health check (1 test)..."
	. .venv/bin/activate && pytest \
		tests/test_render_deployment.py::test_step_05_r3_synthesis_completes \
		-v