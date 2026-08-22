# Architecture Decision Record: Modular Monolith

**ADR-001** | Date: 2024-01-15

## Status

Accepted

## Context

We need to choose an architectural style for the ERP03 enterprise resource planning system that balances:
- Development velocity and simplicity
- Operational complexity
- Team organization and ownership
- Scalability requirements
- Time to market

### Constraints

- Limited DevOps resources initially
- Need for rapid iteration in early stages
- Multiple business domains (Finance, HCM, SCM, MFG, CRM)
- Eventual need for independent scaling of components
- Compliance and audit requirements

## Decision

We will adopt a **Modular Monolith** architecture with the following characteristics:

### Structure

1. **Single Codebase**: All modules in one repository
2. **Logical Separation**: Clear boundaries between business domains
3. **Database Schema Separation**: Each module uses its own PostgreSQL schema
4. **Event-Driven Communication**: Asynchronous messaging via RabbitMQ for inter-module events
5. **Shared Infrastructure**: Common database, cache, and message broker

### Module Boundaries

```
apps/erp/
├── modules/
│   ├── finance/      # Accounting, general ledger
│   ├── hcm/          # Human capital management
│   ├── scm/          # Supply chain management
│   ├── mfg/          # Manufacturing
│   └── crm/          # Customer relationship management
├── core/modules/     # Shared domain services
│   ├── accounting/
│   ├── sales/
│   ├── inventory/
│   ├── hr/
│   ├── warehouse/
│   ├── logistics/
│   └── reporting/
```

### Database Schema Design

Each business domain has its own schema:
- `accounting`, `sales`, `inventory`, `hr`, `crm`, `warehouse`, `logistics`, `reporting`

Benefits:
- Logical isolation without physical separation
- Easy to extract to separate databases later
- Simplified transactions within modules
- Clear ownership boundaries

## Consequences

### Positive

✅ **Development Simplicity**
- Single deployment pipeline
- Easier local development setup
- Simplified testing (no network mocking needed)
- Atomic commits across modules

✅ **Operational Efficiency**
- One application to monitor and deploy
- Reduced infrastructure costs initially
- Simpler CI/CD pipelines
- Easier debugging (no distributed tracing needed yet)

✅ **Team Organization**
- Clear module ownership
- Independent development within modules
- Shared understanding of codebase

✅ **Evolutionary Path**
- Can extract modules to microservices when needed
- Database schemas can be migrated to separate databases
- Event-driven design facilitates decoupling

### Negative

❌ **Scalability Limitations**
- Cannot scale individual modules independently
- Resource contention possible under heavy load
- Single point of failure (mitigated by health checks and circuit breakers)

❌ **Code Coupling Risk**
- Requires discipline to maintain module boundaries
- Potential for "big ball of mud" without proper governance
- Need for architectural reviews

❌ **Deployment Coupling**
- All modules deployed together
- Risk of one module breaking others
- Requires comprehensive testing

## Migration Strategy

### Phase 1: Modular Monolith (Current)
- Implement all modules in single codebase
- Establish clear boundaries and contracts
- Build event-driven communication patterns

### Phase 2: Service Extraction (When Needed)
Criteria for extraction:
- Module requires independent scaling
- Team size exceeds Dunbar's number (~15 developers)
- Specific compliance requirements
- Performance bottlenecks

Extraction process:
1. Ensure module communicates only via events/APIs
2. Migrate database schema to dedicated database
3. Create separate deployment pipeline
4. Deploy as independent microservice

## Governance

### Code Review Requirements
- Any cross-module dependency requires architectural review
- Module APIs must be versioned and documented
- Events must follow standard schema

### Testing Requirements
- Unit tests for each module
- Integration tests for module interactions
- End-to-end tests for critical workflows

### Monitoring Requirements
- Per-module metrics and dashboards
- Distributed tracing ready (request IDs)
- Health checks for each module

## Alternatives Considered

### Option 1: Microservices from Start
**Rejected because:**
- High operational complexity
- Requires mature DevOps practices
- Slower initial development
- Overkill for current team size and traffic

### Option 2: Traditional Monolith
**Rejected because:**
- No clear module boundaries
- Difficult to extract services later
- Tight coupling inevitable

### Option 3: Domain-Driven Monolith
**Considered but Modular Monolith chosen because:**
- More explicit about database separation
- Better preparation for eventual service extraction
- Clearer alignment with business domains

## References

- [Modular Monolith vs Microservices](https://www.youtube.com/watch?v=y8OnoxKotPQ)
- [Domain-Driven Design](https://domainlanguage.com/ddd/)
- [Building Evolutionary Architectures](https://www.oreilly.com/library/view/building-evolutionary-architectures/9781491986363/)

---

**Next Review Date**: 2024-07-15 or when any module reaches 10k+ daily active users
