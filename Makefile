.PHONY: test lint fmt validate deploy clean

# ── Development ──

test:
	python -m pytest tests/ -v --tb=short

test-cov:
	python -m pytest tests/ -v --tb=short --cov=src --cov-report=term-missing

lint:
	ruff check src/ tests/

fmt:
	ruff format src/ tests/

# ── Terraform ──

validate:
	cd terraform && terraform init -backend=false && terraform validate

plan:
	cd terraform && terraform plan

deploy:
	cd terraform && terraform apply -auto-approve

destroy:
	cd terraform && terraform destroy

# ── Packaging ──

package:
	mkdir -p terraform/.build
	cd src && zip -r ../terraform/.build/lambda.zip . -x "__pycache__/*" "*.pyc"

clean:
	rm -rf terraform/.build
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
