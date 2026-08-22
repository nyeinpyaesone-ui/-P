# ERP03 Enterprise Resource Planning System

[![CI/CD](https://github.com/nyeinpyaesone-ui/-P/actions/workflows/blank.yml/badge.svg)](https://github.com/nyeinpyaesone-ui/-P/actions)
[![Docker](https://github.com/nyeinpyaesone-ui/-P/actions/workflows/docker.yml/badge.svg)](https://github.com/nyeinpyaesone-ui/-P/pkgs/container/-P)
[![Deploy to Render](https://github.com/nyeinpyaesone-ui/-P/actions/workflows/render-deploy.yml/badge.svg)](https://erp03.onrender.com)

Complete enterprise resource planning system with modular architecture for accounting, sales, inventory, HR, CRM, warehouse, logistics, and reporting.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 20+ (for frontend development)

### Bootstrap the System

```bash
# Clone the repository
git clone https://github.com/nyeinpyaesone-ui/-P.git
cd -P

# Run the bootstrap orchestrator
python scripts/bootstrap.py

# Or use make
make bootstrap
```

### Manual Setup

```bash
# Copy environment file
cp .env.example .env

# Build and start all services
docker compose up -d --build

# View logs
docker compose logs -f
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      ERP03 System                            │
├─────────────────────────────────────────────────────────────┤
│  Frontend Layer                                              │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │  Admin UI    │  │  Client UI   │                         │
│  │  (Port 3000) │  │  (Port 3001) │                         │
│  └──────────────┘  └──────────────┘                         │
├─────────────────────────────────────────────────────────────┤
│  Application Layer                                           │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │ ERP Backend  │  │ AI Platform  │                         │
│  │  (Port 8000) │  │  (Port 8001) │                         │
│  └──────────────┘  └──────────────┘                         │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │    Redis     │  │   RabbitMQ   │      │
│  │  (Port 5432) │  │  (Port 6379) │  │  (Port 5672) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Modules

| Module | Schema | Description |
|--------|--------|-------------|
| Accounting | `accounting` | General ledger, financial reporting |
| Sales | `sales` | Orders, invoices, customer management |
| Inventory | `inventory` | Stock tracking, product management |
| HR | `hr` | Employee management, payroll |
| CRM | `crm` | Customer relationships, pipelines |
| Warehouse | `warehouse` | Warehouse operations, picking |
| Logistics | `logistics` | Supply chain, transportation |
| Reporting | `reporting` | Analytics, BI dashboards |

## 🔧 Makefile Commands

```bash
make help          # Show all available commands
make bootstrap     # Run full bootstrap orchestrator
make build         # Build all Docker containers
make up            # Start all services
make down          # Stop all services
make logs          # View all logs
make test          # Run tests
make clean         # Remove containers and volumes
```

## 🌐 API Endpoints

- **ERP Backend**: http://localhost:8000
  - Health: http://localhost:8000/healthz
  - API Docs: http://localhost:8000/docs
  
- **AI Platform**: http://localhost:8001
  - Health: http://localhost:8001/healthz
  - API Docs: http://localhost:8001/docs

- **Admin UI**: http://localhost:3000
- **Client UI**: http://localhost:3001

## 🔄 CI/CD Pipeline

### GitHub Actions Workflows

1. **CI Workflow** (`.github/workflows/blank.yml`)
   - Runs on push/PR to main
   - Builds and validates code

2. **Docker Workflow** (`.github/workflows/docker.yml`)
   - Multi-platform builds (amd64/arm64)
   - Pushes to GHCR on version tags
   - Image signing with Cosign

3. **Render Deploy** (`.github/workflows/render-deploy.yml`)
   - Auto-deploys to Render on main branch push
   - Manual deployment option
   - Environment variable support

### Deployment Status

- **Production**: [erp03.onrender.com](https://erp03.onrender.com)
- **Service ID**: `srv-da1vjkc9v7es738de6ag`

## 🔐 Security

- All passwords must be changed from defaults in `.env`
- Use strong `SECRET_KEY` for production
- Enable HTTPS in production
- Regular security updates via Dependabot

## 📝 Development

### Local Development

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend/admin && npm install
cd ../client && npm install

# Start infrastructure only
docker compose up -d postgres redis rabbitmq

# Run backend locally
python -m uvicorn apps.erp.main:app --reload

# Run frontend locally
cd frontend/admin && npm run dev
```

### Running Tests

```bash
# Run all tests
make test

# Run specific module tests
pytest apps/erp/core/modules/accounting/tests/ -v
```

## 🛠️ Troubleshooting

### Bootstrap Fails

```bash
# Force re-bootstrap
python scripts/bootstrap.py --force

# Or repair packages
python scripts/bootstrap.py --repair-packages
```

### Database Connection Issues

```bash
# Check database logs
docker compose logs postgres

# Reset database volume
docker compose down -v
docker compose up -d postgres
```

### Service Not Starting

```bash
# Check service status
docker compose ps

# View specific service logs
docker compose logs erp-backend

# Rebuild and restart
docker compose up -d --build erp-backend
```

## 📄 License

MIT License - see LICENSE file for details

## 👥 Support

- Documentation: `/docs` directory
- Issues: GitHub Issues
- Production Support: Contact DevOps team

---

**Built with** FastAPI, PostgreSQL, Redis, RabbitMQ, React, Next.js
