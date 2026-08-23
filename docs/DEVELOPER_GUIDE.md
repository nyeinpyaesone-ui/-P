# Developer Guide

Quick start guide for setting up and developing on ERP03.

## Prerequisites

- Python 3.11 or 3.12
- Docker & Docker Compose
- Node.js 20+ (for frontend development)
- Git

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/nyeinpyaesone-ui/-P.git
cd -P
```

### 2. Environment Configuration

```bash
cp .env.example .env
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))" >> .env
python -c "import secrets; print('POSTGRES_PASSWORD=' + secrets.token_urlsafe(16))" >> .env
python -c "import secrets; print('RABBITMQ_DEFAULT_PASS=' + secrets.token_urlsafe(16))" >> .env
```

### 3. Start Infrastructure Services

```bash
docker compose up -d postgres redis rabbitmq
docker compose ps
```

### 4. Install Python Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Run Database Migrations

```bash
export $(cat .env | xargs)
alembic upgrade head
```

### 6. Start Development Server

```bash
python -m uvicorn apps.erp.main:app --reload --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000/docs for API documentation.

## Running Tests

```bash
pytest apps/ -v
pytest apps/ -v --cov=apps --cov-report=html
```

## Code Quality

```bash
black apps/ scripts/
isort apps/ scripts/
flake8 apps/ scripts/
mypy apps/ --ignore-missing-imports
```

## Working with Modules

Each module follows this structure:

```
modules/finance/
├── __init__.py
├── models.py
├── schemas.py
├── router.py
└── service.py
```

## Next Steps

- Read [Architecture Overview](./architecture/OVERVIEW.md)
- Review [API Contracts](./api-contracts/STANDARD_RESPONSES.md)
- Study [ADR documents](./adr/)
