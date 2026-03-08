# ⚡ CloudTask API — Serverless Task Processing

[![CI](https://github.com/kelsonbrito50/cloudtask-api/actions/workflows/ci.yml/badge.svg)](https://github.com/kelsonbrito50/cloudtask-api/actions)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Terraform](https://img.shields.io/badge/IaC-Terraform-purple)
![AWS](https://img.shields.io/badge/Cloud-AWS-orange)
![Tests](https://img.shields.io/badge/tests-20%20passed-brightgreen)

A **serverless REST API** with event-driven task processing, deployed 100% with **Terraform**. Zero servers to manage.

## Architecture

```
Client → API Gateway (HTTP) → Lambda (CRUD) → DynamoDB
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
| **API** | API Gateway v2 (HTTP API) |
| **Database** | DynamoDB (PAY_PER_REQUEST, encrypted, PITR) |
| **Queue** | SQS + Dead Letter Queue (3 retries) |
| **Notifications** | SNS (email on completion) |
| **Monitoring** | CloudWatch (logs + DLQ alarm) |
| **IaC** | Terraform (8 config files) |
| **CI/CD** | GitHub Actions (lint + test + terraform validate) |
| **Security** | IAM least-privilege (separate API vs Worker roles) |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/tasks` | Create task (queues for processing) |
| `GET` | `/tasks` | List tasks (`?status=pending`) |
| `GET` | `/tasks/{id}` | Get single task |
| `PUT` | `/tasks/{id}` | Update task fields |
| `DELETE` | `/tasks/{id}` | Delete task |

### Create Task

```bash
curl -X POST https://YOUR-API-URL/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Process report", "priority": "high"}'
```

```json
{
  "task_id": "550e8400-e29b-...",
  "title": "Process report",
  "priority": "high",
  "status": "pending",
  "created_at": "2026-03-08T22:30:00+00:00"
}
```

### Event Flow

1. **Client** → `POST /tasks`
2. **Create Lambda** validates, stores in DynamoDB, sends to SQS
3. **SQS** delivers to Worker Lambda (batch of 5)
4. **Worker** processes task, updates status to `completed`
5. **SNS** sends email notification
6. **CloudWatch** monitors errors; DLQ catches failures after 3 retries

## Infrastructure (Terraform)

```
terraform/
├── main.tf           # Provider config
├── variables.tf      # Configurable parameters
├── outputs.tf        # API URL, table name, queue URLs
├── api_gateway.tf    # HTTP API + routes + integrations
├── lambda.tf         # 6 Lambda functions + SQS trigger
├── dynamodb.tf       # Table + GSI + encryption + PITR
├── sqs.tf            # Queue + DLQ + redrive policy
├── sns.tf            # Notification topic + email sub
├── iam.tf            # Separate least-privilege roles (API vs Worker)
└── cloudwatch.tf     # Log groups + DLQ alarm
```

### Security Highlights

- **Separate IAM Roles** — API Lambdas and Worker Lambda have different permissions
- **Least Privilege** — API can't publish to SNS; Worker can't send to SQS
- **Encryption at Rest** — DynamoDB server-side encryption
- **Point-in-Time Recovery** — DynamoDB PITR enabled
- **Dead Letter Queue** — 3 retries before DLQ, alarm on messages
- **CORS** — Configured at API Gateway level

## Development

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run tests (20 tests)
make test

# Lint
make lint

# Format
make fmt
```

## Deploy

```bash
# Initialize Terraform
make tf-init

# Preview changes
make tf-plan

# Deploy to AWS
make tf-apply
```

## Project Structure

```
cloudtask-api/
├── terraform/              # Infrastructure as Code
├── src/
│   ├── handlers/
│   │   ├── create_task.py  # POST /tasks
│   │   ├── get_task.py     # GET /tasks/{id}
│   │   ├── list_tasks.py   # GET /tasks
│   │   ├── update_task.py  # PUT /tasks/{id}
│   │   ├── delete_task.py  # DELETE /tasks/{id}
│   │   └── process_task.py # SQS consumer (worker)
│   └── utils/
│       ├── response.py     # Standardized responses
│       └── logger.py       # Structured logging
├── tests/
│   ├── conftest.py         # Mocked AWS (moto)
│   ├── test_create_task.py # 10 tests
│   ├── test_get_task.py    # 3 tests
│   ├── test_list_tasks.py  # 4 tests
│   └── test_process_task.py# 3 tests
├── .github/workflows/
│   └── ci.yml              # Lint + test + terraform validate
├── Makefile
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml
```

## Skills Proven

| Skill | Evidence |
|---|---|
| **Terraform** | 8 `.tf` files, full AWS infra |
| **Infrastructure as Code** | CI validates terraform on every push |
| **AWS Lambda** | 6 functions (5 CRUD + 1 worker) |
| **Microservices** | Each Lambda = independent service |
| **Cloud Security** | Separate IAM roles, least-privilege, encryption |
| **Cloud Computing** | API Gateway + Lambda + DynamoDB + SQS + SNS + CloudWatch |
| **Event-Driven** | SQS → Lambda → SNS notification chain |
| **Observability** | CloudWatch logs + DLQ alarm |
| **Python** | Handlers in Python 3.12 |
| **CI/CD** | GitHub Actions: lint + test + terraform validate |
| **TDD** | 20 tests with moto mocks |

## Author

**Kelson Brito** — Full Stack Developer

- [GitHub](https://github.com/kelsonbrito50)
- [LinkedIn](https://www.linkedin.com/in/kelson-brito-ba922b363)

## License

MIT
