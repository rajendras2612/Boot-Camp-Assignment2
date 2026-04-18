.PHONY: help install run test shell

help:
	@echo "Available commands:"
	@echo "  make install        - install Python dependencies"
	@echo "  make run            - run the FastAPI server locally"
	@echo "  make test           - run pytest"
	@echo "  make publish-hf     - publish sample model folder to Hugging Face"
	@echo "  make shell          - open a shell in the Python environment"

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

test:
	pytest

publish-hf:
	python3 -m pip install --upgrade pip
	pip install -r requirements.txt
	python scripts/publish_hf_model.py --repo-id your-username/your-model-name --path ./model --token "$$HF_TOKEN"

shell:
	python3 -m venv .venv
	. .venv/bin/activate && bash
