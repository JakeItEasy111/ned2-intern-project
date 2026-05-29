# Makefile in project root
.PHONY: dev setup

setup:
	cd api && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

dev:
	cd api && source .venv/bin/activate && uvicorn main:app --reload --port 8000