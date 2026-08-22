# ERP03 v1.0.0 - Enterprise Resource Planning System

## 📋 Project Requirements

### 1. Functional Requirements

#### 1.1 Finance & Accounting Module
- **General Ledger (GL)**: Chart of accounts, journal entries, financial statements
- **Accounts Payable (AP)**: Vendor management, invoice processing, payment tracking
- **Accounts Receivable (AR)**: Customer invoicing, payment collection, aging reports
- **Cash Management**: Bank reconciliation, cash flow forecasting, liquidity management
- **Fixed Assets**: Asset registration, depreciation calculation, disposal tracking
- **Budgeting**: Budget creation, variance analysis, approval workflows

#### 1.2 Human Capital Management (HCM)
- **Employee Directory**: Centralized employee records, organizational hierarchy
- **Payroll Processing**: Salary calculation, tax withholding, benefits administration
- **Time & Attendance**: Timesheet management, leave tracking, overtime calculation
- **Performance Management**: Goal setting, performance reviews, competency tracking
- **Recruitment**: Job postings, applicant tracking, onboarding workflows
- **Training & Development**: Course management, skill tracking, certification records

#### 1.3 Supply Chain Management (SCM)
- **Inventory Management**: Stock levels, warehouse locations, inventory valuation
- **Procurement**: Purchase requisitions, vendor selection, purchase orders
- **Order Management**: Sales orders, order fulfillment, shipping coordination
- **Logistics**: Shipment tracking, carrier management, delivery scheduling
- **Warehouse Operations**: Receiving, put-away, picking, packing, shipping
- **Demand Planning**: Forecasting, safety stock calculation, reorder points

#### 1.4 Manufacturing (MRP)
- **Bill of Materials (BOM)**: Multi-level BOMs, routing definitions, cost roll-up
- **Production Planning**: Master production schedule, capacity planning, material requirements
- **Work Orders**: Production orders, shop floor control, quality inspections
- **Quality Control**: Quality standards, inspection plans, non-conformance tracking
- **Costing**: Standard costing, actual costing, variance analysis
- **Maintenance**: Preventive maintenance, work orders, asset downtime tracking

#### 1.5 Customer Relationship Management (CRM)
- **Contact Management**: Customer profiles, interaction history, communication logs
- **Sales Pipeline**: Lead management, opportunity tracking, sales forecasting
- **Marketing Campaigns**: Campaign planning, execution tracking, ROI analysis
- **Customer Service**: Case management, SLA tracking, knowledge base
- **Quotes & Proposals**: Quote generation, approval workflows, conversion tracking
- **Analytics**: Customer segmentation, churn analysis, lifetime value calculation

### 2. Non-Functional Requirements

#### 2.1 Performance
- **Response Time**: API responses < 200ms for standard operations
- **Throughput**: Support 1000+ concurrent users
- **Scalability**: Horizontal scaling capability for all services
- **Database**: Query optimization, indexing strategy, connection pooling

#### 2.2 Security
- **Authentication**: JWT-based authentication with refresh tokens
- **Authorization**: Role-based access control (RBAC) with granular permissions
- **Data Encryption**: TLS 1.3 for data in transit, AES-256 for data at rest
- **Audit Trails**: Immutable logs for all create, update, delete operations
- **Compliance**: GDPR, SOC2, ISO 27001 alignment

#### 2.3 Reliability
- **Availability**: 99.9% uptime SLA
- **Disaster Recovery**: RPO < 1 hour, RTO < 4 hours
- **Backup Strategy**: Daily automated backups with 30-day retention
- **Failover**: Automatic failover for critical services

#### 2.4 Maintainability
- **Code Quality**: >80% test coverage, static code analysis
- **Documentation**: API documentation, deployment guides, user manuals
- **Versioning**: Semantic versioning for all components
- **Monitoring**: Real-time monitoring with alerting capabilities

### 3. Technical Requirements

#### 3.1 Technology Stack
- **Backend Runtime**: Python 3.12.13-slim (Debian Trixie)
- **Web Framework**: FastAPI 0.115.0
- **ASGI Server**: Uvicorn 0.30.6
- **ORM**: SQLAlchemy 2.0.36 (Async)
- **Task Queue**: Celery 5.6.0 with RabbitMQ
- **Database**: PostgreSQL 15.8 (ACID compliant)
- **Cache**: Redis 7.4
- **Search**: Elasticsearch 8.x (optional module)
- **Frontend**: Next.js 14.x with TypeScript
- **Containerization**: Docker 24.x with BuildKit
- **Orchestration**: Kubernetes 1.28+ (optional)

#### 3.2 Architecture Patterns
- **Modular Monolith**: Domain-driven design with clear module boundaries
- **Event-Driven**: Async communication via RabbitMQ for inter-module events
- **CQRS**: Command Query Responsibility Segregation for complex queries
- **Microservices Ready**: Modular design allowing future service extraction

#### 3.3 Infrastructure Requirements
- **Container Registry**: GitHub Container Registry (GHCR)
- **CI/CD**: GitHub Actions with automated testing and image signing
- **Secrets Management**: GitHub Secrets for CI/CD, environment variables for runtime
- **Logging**: Structured JSON logging with correlation IDs
- **Metrics**: Prometheus-compatible metrics endpoint
- **Tracing**: OpenTelemetry integration (optional)

---

## 🧩 System Components

### 1. Core Application Layer

#### 1.1 Backend Services (`apps/erp/`)
```
apps/erp/
├── main.py                 # FastAPI application entry point
├── core/                   # Core framework components
│   ├── config/            # Configuration management
│   ├── database/          # Database connections, sessions
│   ├── security/          # Authentication, authorization
│   └── logging/           # Structured logging setup
├── modules/               # Business domain modules
│   ├── finance/           # Finance & Accounting
│   ├── hcm/               # Human Capital Management
│   ├── scm/               # Supply Chain Management
│   ├── manufacturing/     # Manufacturing & MRP
│   └── crm/               # Customer Relationship Management
├── api/                   # API layer
│   └── v1/                # Versioned API endpoints
├── engine/                # Business logic engine
│   ├── commands/          # CQRS commands
│   ├── queries/           # CQRS queries
│   └── events/            # Domain events
└── tasks/                 # Celery background tasks
```

**Key Components:**
- **`main.py`**: FastAPI application with CORS, middleware, lifespan events
- **`core/database/session.py`**: Async SQLAlchemy session factory
- **`core/security/jwt.py`**: JWT token generation and validation
- **`modules/finance/models.py`**: GL, AP, AR, Cash Management models
- **`modules/hcm/models.py`**: Employee, Payroll, Performance models
- **`modules/scm/models.py`**: Inventory, Procurement, Logistics models
- **`modules/manufacturing/models.py`**: BOM, Work Orders, Quality models
- **`modules/crm/models.py`**: Contacts, Opportunities, Cases models
- **`tasks/finance_tasks.py`**: Background jobs for financial processing
- **`engine/events/dispatcher.py`**: Event bus for inter-module communication

#### 1.2 Frontend Applications

**Admin Dashboard (`frontend/admin/`)**
```
frontend/admin/
├── app/                   # Next.js App Router
│   ├── layout.tsx         # Root layout with auth provider
│   ├── page.tsx           # Dashboard home
│   ├── finance/           # Finance module pages
│   ├── hcm/               # HCM module pages
│   ├── scm/               # SCM module pages
│   ├── manufacturing/     # Manufacturing module pages
│   └── crm/               # CRM module pages
├── components/            # Reusable UI components
│   ├── DataTable.tsx      # Generic data table with sorting/filtering
│   ├── FormInput.tsx      # Form input components
│   ├── Charts/            # Visualization components
│   └── Layout/            # Navigation, sidebar, header
├── lib/                   # Utility functions
│   ├── api.ts             # API client with auth
│   └── utils.ts           # Helper functions
└── public/                # Static assets
```

**Client Portal (`frontend/client/`)**
```
frontend/client/
├── app/
│   ├── layout.tsx
│   ├── page.tsx           # Client home
│   ├── orders/            # Order tracking
│   ├── invoices/          # Invoice viewing
│   └── support/           # Support tickets
├── components/
│   ├── OrderTracker.tsx   # Real-time order status
│   └── InvoiceViewer.tsx  # Invoice display
└── lib/
    └── api.ts
```

### 2. Infrastructure Layer

#### 2.1 Docker Configuration
```
Dockerfile.backend         # Multi-stage build for Python backend
Dockerfile.frontend        # Multi-stage build for Next.js frontend
docker-compose.yml         # Local development orchestration
docker-compose.prod.yml    # Production configuration
```

**Dockerfile.backend Features:**
- Base: `python:3.12.13-slim`
- Non-root user: `appuser` (UID 1000)
- Health check: `/healthz` endpoint
- Entrypoint: Migration + Uvicorn startup
- Labels: OCI-compliant metadata

**Dockerfile.frontend Features:**
- Base: `node:20-alpine`
- Multi-stage: Build → Standalone output
- Health check: HTTP check on port 3000
- Optimized: Minimal production image

#### 2.2 Database Schema
```
infrastructure/postgres/
└── init.sql               # Database initialization

Schemas:
- accounting               # Finance module tables
- hcm                      # HR module tables
- scm                      # Supply chain tables
- manufacturing            # Production tables
- crm                      # Customer relations tables
- audit                    # Audit trail tables
- shared                   # Shared reference data
```

**Key Tables per Schema:**
- **accounting**: `accounts`, `journal_entries`, `transactions`, `vendors`, `customers`
- **hcm**: `employees`, `departments`, `payroll_runs`, `leave_requests`
- **scm**: `products`, `warehouses`, `purchase_orders`, `sales_orders`, `shipments`
- **manufacturing**: `boms`, `work_orders`, `routings`, `quality_inspections`
- **crm**: `contacts`, `opportunities`, `cases`, `interactions`
- **audit**: `audit_logs`, `change_history`

#### 2.3 Message Broker (RabbitMQ)
```
Queues:
- finance.process_payment   # Payment processing
- hcm.run_payroll          # Payroll calculation
- scm.update_inventory     # Inventory synchronization
- manufacturing.schedule_production  # Production planning
- crm.send_notification    # Customer notifications

Exchanges:
- erp.events               # Domain events fanout
- erp.tasks                # Task distribution
```

### 3. DevOps & Automation Layer

#### 3.1 CI/CD Workflows
```
.github/workflows/
├── docker.yml             # Build, sign, push Docker images
├── ci.yml                 # Run tests, linting, type checking
└── release.yml            # Create releases on version tags
```

**docker.yml Pipeline:**
1. Checkout code
2. Set up Docker Buildx
3. Login to GHCR
4. Build multi-arch images (amd64, arm64)
5. Sign images with Cosign
6. Push to GHCR
7. Generate SBOM

#### 3.2 Setup Scripts
```
scripts/
├── env-setup.sh           # Validate environment prerequisites
├── sprint-setup.sh        # Install dependencies, prepare dev env
├── init.sh                # Full system initialization
├── bootstrap.py           # Production bootstrap orchestrator
└── run_migrations.sh      # Database migration helper
```

**Bootstrap Orchestrator Features:**
- Artifact validation
- Environment resolution
- Package structure repair
- Image building
- Infrastructure startup
- Migration application
- Seed data loading
- Health verification
- Atomic rollback on failure

### 4. Security & Compliance Components

#### 4.1 Authentication & Authorization
- **JWT Provider**: RS256 signed tokens with 15-minute expiry
- **Refresh Tokens**: 7-day expiry with rotation
- **RBAC Engine**: Role-permission mapping with hierarchical roles
- **API Keys**: Service-to-service authentication

#### 4.2 Audit Trail System
- **Immutable Logs**: Append-only audit log table
- **Change Tracking**: Before/after snapshots for critical entities
- **User Attribution**: All actions linked to user identity
- **Retention Policy**: Configurable retention periods

#### 4.3 Data Protection
- **Soft Deletes**: `is_deleted` flag with cascade filtering
- **Encryption at Rest**: Database-level encryption for sensitive fields
- **Masking**: PII masking in logs and non-production environments
- **Access Controls**: Row-level security for multi-tenant scenarios

### 5. Observability Components

#### 5.1 Logging
- **Structured Format**: JSON logs with timestamps, levels, context
- **Correlation IDs**: Request tracing across services
- **Log Aggregation**: Compatible with ELK, Loki, Datadog
- **Sensitive Data Filtering**: Automatic PII redaction

#### 5.2 Metrics
- **Prometheus Endpoint**: `/metrics` with business and system metrics
- **Key Metrics**:
  - Request latency (p50, p95, p99)
  - Error rates by endpoint
  - Database connection pool usage
  - Queue depths
  - Business KPIs (orders processed, invoices generated)

#### 5.3 Health Checks
- **Liveness Probe**: `/healthz` - Basic service availability
- **Readiness Probe**: `/readyz` - Dependencies connected
- **Startup Probe**: `/startupz` - Initialization complete
- **Detailed Status**: Component-level health reporting

---

## 📦 Deliverables

### Code Artifacts
- [x] Backend application with 5 ERP modules
- [x] Admin dashboard (Next.js)
- [x] Client portal (Next.js)
- [x] Database schemas and migrations
- [x] Docker configurations
- [x] CI/CD workflows
- [x] Setup scripts

### Documentation
- [x] README.md (project overview)
- [x] API documentation (OpenAPI/Swagger)
- [x] Deployment guide
- [x] Module-specific documentation

### Quality Assurance
- [x] Unit tests (pytest)
- [x] Integration tests
- [x] End-to-end tests (Playwright)
- [x] Security scanning (Trivy)
- [x] Code quality checks (ruff, mypy)

---

## 🚀 Usage Instructions

### Quick Start
```bash
# 1. Validate environment
./scripts/env-setup.sh

# 2. Setup development environment
./scripts/sprint-setup.sh

# 3. Initialize full system
./scripts/init.sh
```

### Access Points
- **ERP API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Admin Dashboard**: http://localhost:3000
- **Client Portal**: http://localhost:3001

### Docker Images
After CI/CD pipeline runs:
- **Backend**: `ghcr.io/nyeinpyaesone-ui/-P/erp-backend:main`
- **Frontend Admin**: `ghcr.io/nyeinpyaesone-ui/-P/frontend-admin:main`
- **Frontend Client**: `ghcr.io/nyeinpyaesone-ui/-P/frontend-client:main`
