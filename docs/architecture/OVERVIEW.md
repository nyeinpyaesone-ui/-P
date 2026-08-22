# ERP03 Architecture Overview

## System Architecture

ERP03 follows a **Modular Monolith** architecture with event-driven capabilities, providing the simplicity of a monolith with the organizational benefits of microservices.

### Architectural Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Admin UI    │  │  Client UI   │  │   API Docs   │      │
│  │  React/Next  │  │  React/Next  │  │   FastAPI    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  FastAPI Backend                      │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │   │
│  │  │Finance  │ │  HCM    │ │  SCM    │ │  MFG    │    │   │
│  │  │ Module  │ │ Module  │ │ Module  │ │ Module  │    │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘    │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │   │
│  │  │  CRM    │ │Account- │ │ Sales   │ │Inventory│    │   │
│  │  │ Module  │ │ ing     │ │ Module  │ │ Module  │    │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    Core Services Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Observability│  │  Resilience  │  │   Service    │      │
│  │  (Logging)   │  │  (Patterns)  │  │   Registry   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
├─────────────────────────────────────────────────────────────┤
│                    Infrastructure Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │    Redis     │  │   RabbitMQ   │      │
│  │  (Database)  │  │   (Cache)    │  │  (Messaging) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Design Principles

### 1. Modular Monolith
- **Single deployment unit** with clear module boundaries
- **Logical separation** via database schemas
- **Shared infrastructure** reducing operational complexity
- **Event-driven communication** between modules

### 2. Database Schema Separation
Each business domain has its own PostgreSQL schema:
- `accounting` - General ledger, financial reporting
- `sales` - Orders, invoices, customer management
- `inventory` - Stock tracking, product management
- `hr` - Employee management, payroll
- `crm` - Customer relationships, pipelines
- `warehouse` - Warehouse operations, picking
- `logistics` - Supply chain, transportation
- `reporting` - Analytics, BI dashboards

### 3. Event-Driven Architecture
- **RabbitMQ** for asynchronous inter-module communication
- **Redis** for caching and pub/sub messaging
- **Event sourcing** capability for audit trails

### 4. Defense in Depth Security
- **Required environment variables** for secrets (no defaults in production)
- **Restrictive CORS** configuration
- **Security headers** on all responses
- **Non-root container** execution
- **Signed Docker images** with Cosign

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | React, Next.js | Admin & Client UIs |
| API | FastAPI | RESTful API framework |
| Database | PostgreSQL 15 | Primary data store |
| Cache | Redis 7 | Session cache, rate limiting |
| Messaging | RabbitMQ 3 | Event bus, async tasks |
| ORM | SQLAlchemy 2.0 | Database abstraction |
| Validation | Pydantic 2.0 | Data validation |
| Auth | python-jose, passlib | JWT authentication |
| Logging | structlog | Structured JSON logging |
| Monitoring | Prometheus | Metrics collection |
| Testing | pytest, httpx | Unit & integration tests |
| Code Quality | black, flake8, mypy | Linting & type checking |

## Module Structure

```
apps/erp/
├── main.py                 # Application entry point
├── api/
│   └── v1/
│       ├── health.py       # Health check endpoints
│       └── __init__.py
├── core/                   # Cross-cutting concerns
│   ├── observability.py    # Logging, tracing, security headers
│   ├── resilience.py       # Circuit breaker, retry patterns
│   ├── services.py         # Service registry, health checks
│   └── modules/            # Core business modules
│       ├── accounting/
│       ├── sales/
│       ├── inventory/
│       ├── hr/
│       ├── crm/
│       ├── warehouse/
│       ├── logistics/
│       └── reporting/
├── modules/                # High-level module routers
│   ├── finance/
│   ├── hcm/
│   ├── scm/
│   ├── mfg/
│   └── crm/
├── framework/              # Framework configuration
│   ├── config/
│   │   └── settings.py     # Centralized configuration
│   └── database/
│       └── models.py       # Base models
└── engine/                 # CLI commands
    └── commands/
        └── seed.py         # Database seeding
```

## Communication Patterns

### Synchronous (HTTP/REST)
- External API calls
- Real-time user requests
- Health checks

### Asynchronous (Message Queue)
- Inter-module events
- Background job processing
- Eventual consistency workflows

### Caching Strategy
- **L1 Cache**: Application-level caching with Redis
- **L2 Cache**: Database query result caching
- **Session Storage**: Redis-backed user sessions

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                    │
│  ┌───────────────────────────────────────────────────┐  │
│  │               Ingress Controller                   │  │
│  └───────────────────────────────────────────────────┘  │
│                          │                               │
│  ┌───────────────────────────────────────────────────┐  │
│  │              Load Balancer Service                 │  │
│  └───────────────────────────────────────────────────┘  │
│           │                    │                         │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │  Backend Pods   │  │  Frontend Pods  │              │
│  │  (HPA scaled)   │  │  (HPA scaled)   │              │
│  └─────────────────┘  └─────────────────┘              │
│           │                                             │
│  ┌───────────────────────────────────────────────────┐  │
│  │           StatefulSet Services                     │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────────────┐   │  │
│  │  │Postgres │  │  Redis  │  │    RabbitMQ     │   │  │
│  │  │  (HA)   │  │ (Cache) │  │   (Messaging)   │   │  │
│  │  └─────────┘  └─────────┘  └─────────────────┘   │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Scalability Considerations

1. **Horizontal Pod Autoscaling (HPA)** based on CPU/memory metrics
2. **Database read replicas** for query scaling
3. **Redis clustering** for cache distribution
4. **RabbitMQ federation** for message routing across regions
5. **Stateless application design** for easy scaling

## Disaster Recovery

- **Automated backups** via Kubernetes CronJobs
- **Point-in-time recovery** with PostgreSQL WAL archiving
- **Multi-region deployment** capability
- **Circuit breakers** preventing cascading failures
- **Health probes** for automatic pod restart

## See Also

- [Architecture Decision Records](../adr/)
- [API Contracts](../api-contracts/)
- [Developer Guide](DEVELOPER_GUIDE.md)
- [Deployment Guide](DEPLOYMENT.md)
