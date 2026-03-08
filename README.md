# ⚡ CloudTask API — Serverless Task Processing

[![CI](https://github.com/kelsonbrito50/cloudtask-api/actions/workflows/ci.yml/badge.svg)](https://github.com/kelsonbrito50/cloudtask-api/actions)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Terraform](https://img.shields.io/badge/IaC-Terraform-purple)
![AWS](https://img.shields.io/badge/Cloud-AWS-orange)
![Tests](https://img.shields.io/badge/tests-22%20passed-brightgreen)

A **serverless REST API** with event-driven task processing, deployed 100% with **Terraform**. Zero servers to manage — just code and infrastructure as code.

## Architecture

```
Client → API Gateway → Lambda (CRUD) → DynamoDB
                           ↓
                       SQS Queue
                           ↓
                  Lambda (Worker) → processes task
                           ↓
                    SNS → email notification
                           ↓
                  CloudWatch → logs + alarms
```

**All infrastructure deployed via Terraform** — no ClickOps, no manual setup.

## Tech Stack

| Layer | Technology |
|---|---|
| **Runtime** | AWS Lambda (Python 3.12) |
| **API** | API Gateway (REST, API key auth) |
| **Database** | DynamoDB (PAY_PER_REQUEST, encrypted, PITR) |
| **Queue** | SQS + Dead Letter Queue (retry with backoff) |
| **Notifications** | SNS (email on task completion) |
| **Monitoring** | CloudWatch (logs, alarms on DLQ + errors) |
| **IaC** | Terraform (S3 backend, DynamoDB lock) |
| **CI/CD** | GitHub Actions (test + lint + terraform validate + deploy) |
| **Security** | IAM least-privilege, encryption at rest, API key auth |

## API Endpoints

All endpoints require `x-api-key` header.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/tasks` | Create a task (queues for processing) |
| `GET` | `/tasks` | List all tasks (optional `?status=` filter) |
| `GET` | `/tasks/{id}` | Get a single task |
| `PUT` | `/tasks/{id}` | Update task fields |
| `DELETE` | `/tasks/{id}` | Delete a task |

### Create Task

```bash
curl -X POST https://api-url/v1/tasks \
  -H "x-api-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Process monthly report",
    "description": "Generate Q1 2026 analytics",
    "priority": "high"
  }'
```

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Process monthly report",
  "priority": "high",
  "status": "pending",
  "created_at": "2026-03-08T22:30:00+00:00"
}
```

### Event Flow

1. **Client** sends `POST /tasks`
2. **Create Lambda** validates, stores in DynamoDB, sends to SQS
3. **SQS** delivers message to Worker Lambda (batch of 5)
4. **Worker Lambda** processes task, updates status to `completed`
5. **SNS** sends email notification on completion
6. **CloudWatch** monitors errors; DLQ catches failures after 3 retries

## Infrastructure (Terraform)

```
terraform/
├── main.tf           # Provider, S3 backend
├── variables.tf      # Configurable parameters
├── outputs.tf        # API URL, ARNs, function names
├── api_gateway.tf    # REST API + routes + API key + usage plan
├── lambda.tf         # 6 Lambda functions + SQS trigger
├── dynamodb.tf       # Table + GSI + encryption + PITR
├── sqs.tf            # Queue + DLQ + redrive policy
├── sns.tf            # Notification topic + email subscription
├── iam.tf            # Least-privilege roles + policies
└── cloudwatch.tf     # Log groups + DLQ alarm + error alarm
```

### Security Highlights

- **IAM Least Privilege** — Each Lambda only gets the permissions it needs
- **Encryption at Rest** — DynamoDB server-side encryption enabled
- **Point-in-Time Recovery** — DynamoDB PITR for data protection
- **Dead Letter Queue** — Failed messages retry 3x, then go to DLQ
- **API Key Auth** — All endpoints require API key via usage plan
- **Rate Limiting** — 5 req/sec sustained, 10 burst, 1000/day quota
- **CloudWatch Alarms** — DLQ messages and Lambda errors trigger SNS alerts

## Development

### Prerequisites

- Python 3.12+
- AWS CLI configured
- Terraform 1.5+

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
make test

# Run tests with coverage
make test-cov

# Lint
make lint

# Format
make fmt
```

### Deploy

```bash
# Validate Terraform
make validate

# Plan changes
make plan

# Apply (deploy to AWS)
make deploy
```

### CI/CD Pipeline

| Job | Trigger | What it does |
|---|---|---|
| **test** | Push/PR to main | Runs pytest |
| **lint** | Push/PR to main | Ruff linter |
| **terraform-validate** | Push/PR to main | `terraform validate` + `fmt -check` |
| **deploy** | Push to main (terraform/ or src/ changes) | `terraform apply` |

## Project Structure

```
cloudtask-api/
├── terraform/              # All infrastructure as code
│   ├── main.tf            
│   ├── variables.tf       
│   ├── outputs.tf         
│   ├── api_gateway.tf     # REST API + routes
│   ├── lambda.tf          # 6 functions + SQS trigger
│   ├── dynamodb.tf        # Table + GSI
│   ├── sqs.tf             # Queue + DLQ
│   ├── sns.tf             # Notifications
│   ├── iam.tf             # Least-privilege IAM
│   └── cloudwatch.tf      # Monitoring + alarms
├── src/
│   ├── handlers/
│   │   ├── create_task.py  # POST /tasks
│   │   ├── get_task.py     # GET /tasks/{id}
│   │   ├── list_tasks.py   # GET /tasks
│   │   ├── update_task.py  # PUT /tasks/{id}
│   │   ├── delete_task.py  # DELETE /tasks/{id}
│   │   └── process_task.py # SQS consumer (worker)
│   ├── models/
│   │   └── task.py         # Task schema + validation
│   └── utils/
│       ├── response.py     # Standardized API responses
│       ├── auth.py         # API key validation
│       └── logger.py       # Structured logging
├── tests/
│   ├── conftest.py         # Mocked AWS (moto)
│   ├── test_create_task.py # 7 tests
│   ├── test_get_task.py    # 3 tests
│   ├── test_list_tasks.py  # 3 tests
│   └── test_process_task.py# 4 tests
├── .github/workflows/
│   ├── ci.yml              # Test + lint + validate
│   └── deploy.yml          # Terraform plan/apply
├── Makefile
├── requirements.txt
├── LICENSE
└── README.md
```

## What This Proves

| Skill | Evidence |
|---|---|
| **Terraform** | Entire infrastructure in `.tf` files |
| **Infrastructure as Code** | `terraform/` directory, CI validates on every PR |
| **AWS Lambda** | 6 Lambda functions (5 CRUD + 1 worker) |
| **Microservices** | Each Lambda = independent, single-responsibility service |
| **Cloud Security** | IAM least-privilege, encryption, DLQ, rate limiting |
| **Cloud Computing** | API Gateway + Lambda + DynamoDB + SQS + SNS + CloudWatch |
| **Event-Driven Design** | SQS → Lambda → SNS notification chain |
| **Observability** | CloudWatch log groups + metric alarms |
| **Python** | All handlers in Python 3.12 with type hints |
| **CI/CD** | GitHub Actions: test + lint + terraform validate + deploy |
| **TDD** | 17+ tests with moto mocks for all AWS services |

## Author

**Kelson Brito** — Full Stack Developer

- [GitHub](https://github.com/kelsonbrito50)
- [LinkedIn](https://www.linkedin.com/in/kelson-brito-ba922b363)

## License

MIT
