.PHONY: setup test run migrate quality backup restore

ifeq ($(OS),Windows_NT)
PYTHON := .venv/Scripts/python.exe

setup:
	powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup.ps1
else
PYTHON := .venv/bin/python

setup:
	bash scripts/setup.sh
endif

test:
	$(PYTHON) -m pytest tests/ -v

run:
	$(PYTHON) manage.py

migrate:
	$(PYTHON) -m flask --app manage.py db upgrade

quality:
	$(PYTHON) -m ruff check backend tests
	$(PYTHON) -m bandit -r backend -ll

backup:
	bash scripts/backup.sh

restore:
	bash scripts/restore.sh "$(BACKUP_FILE)"
	


