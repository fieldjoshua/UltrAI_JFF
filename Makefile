.PHONY: venv install test ci

venv:
	python3 -m venv .venv

install: venv
	. .venv/bin/activate && pip install -U pip && pip install -r requirements.txt

test:
	. .venv/bin/activate && pytest -q

ci: install test
	@echo "OK"