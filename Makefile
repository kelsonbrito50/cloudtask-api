.PHONY: install test lint fmt tf-init tf-plan tf-apply tf-destroy

install:
	pip install -r requirements-dev.txt

test:
	PYTHONPATH=src python -m pytest tests/ -v --tb=short --cov=src

lint:
	ruff check src/ tests/

fmt:
	ruff format src/ tests/
	cd terraform && terraform fmt

tf-init:
	cd terraform && terraform init

tf-plan:
	cd terraform && terraform plan

tf-apply:
	cd terraform && terraform apply

tf-destroy:
	cd terraform && terraform destroy
