# Architecture Decision Record: Database Schema Separation

**ADR-002** | Date: 2024-01-15

## Status

Accepted

## Context

We need to determine the database organization strategy for the ERP03 system that supports:
- Clear domain boundaries
- Independent module evolution
- Data isolation requirements
- Query performance
- Backup and recovery operations
- Future extraction to separate databases

### Current Situation

Multiple business domains with different data characteristics:
- **Accounting**: Financial transactions, strict consistency required
- **Sales**: Orders, invoices, customer data
- **Inventory**: Product stock levels, real-time updates
- **HR**: Employee records, sensitive PII data
- **CRM**: Customer interactions, pipelines
- **Warehouse**: Physical locations, picking operations
- **Logistics**: Shipments, tracking, carrier integration
- **Reporting**: Aggregated data, analytics

## Decision

We will implement **Database Schema Separation** within a single PostgreSQL instance.

### Schema Structure

```sql
CREATE SCHEMA accounting;
CREATE SCHEMA sales;
CREATE SCHEMA inventory;
CREATE SCHEMA hr;
CREATE SCHEMA crm;
CREATE SCHEMA warehouse;
CREATE SCHEMA logistics;
CREATE SCHEMA reporting;
```

### Module-to-Schema Mapping

| Module | Schema | Access Pattern | Sensitivity |
|--------|--------|----------------|-------------|
| Finance | `accounting` | Read-heavy, write-light | High |
| Sales | `sales` | Balanced R/W | Medium |
| Inventory | `inventory` | Write-heavy, real-time | Medium |
| HCM | `hr` | Read-heavy, PII | Very High |
| CRM | `crm` | Read-heavy | Low |
| Warehouse | `warehouse` | Write-heavy | Low |
| Logistics | `logistics` | Balanced R/W | Low |
| Reporting | `reporting` | Read-heavy, aggregations | Low |

### Connection Strategy

Each module connects with schema-specific search_path:

```python
# Example connection URL with schema
DATABASE_URL = "postgresql://user:pass@host:5432/erp_core?options=-c%20search_path%3Daccounting"
```

### Cross-Schema Queries

Allowed patterns:
1. **Explicit schema qualification**: `SELECT * FROM accounting.journal_entries`
2. **Read-only cross-schema views**: For reporting purposes
3. **Foreign keys across schemas**: Allowed but discouraged

Prohibited patterns:
1. **Implicit cross-schema dependencies**: Must be explicit
2. **Schema-level permissions bypass**: Each schema has own roles

## Consequences

### Positive

✅ **Logical Isolation**
- Clear ownership boundaries
- Easier to understand data model
- Simplified refactoring within schemas

✅ **Security Benefits**
- Can grant schema-level permissions
- Easier to audit data access
- PII isolation in `hr` schema

✅ **Operational Flexibility**
- Can backup individual schemas
- Easier to migrate schemas to separate databases
- Independent schema migrations

✅ **Performance Optimization**
- Can tune each schema independently
- Targeted indexing strategies
- Schema-specific connection pooling

✅ **Evolutionary Path**
- Simple to extract schema to dedicated database
- Minimal code changes required
- Gradual migration possible

### Negative

❌ **Shared Resources**
- All schemas share same PostgreSQL instance
- Resource contention possible under load
- Single point of failure

❌ **Complexity Overhead**
- Need to manage schema migrations
- Cross-schema queries require care
- Additional configuration for connections

❌ **Potential for Coupling**
- Developers might create implicit dependencies
- Need governance to prevent schema pollution

## Implementation Guidelines

### Schema Creation

```sql
-- Migration script example
CREATE SCHEMA IF NOT EXISTS accounting AUTHORIZATION erp_admin;
CREATE SCHEMA IF NOT EXISTS sales AUTHORIZATION erp_admin;
-- ... repeat for all schemas
```

### Table Creation

```python
# SQLAlchemy model with schema
class JournalEntry(Base):
    __tablename__ = 'journal_entries'
    __table_args__ = {'schema': 'accounting'}
    
    id = Column(Integer, primary_key=True)
    # ... fields
```

### Migrations

Each schema has independent Alembic migration history:
```
migrations/
├── versions/
│   ├── accounting_001_initial.py
│   ├── sales_001_initial.py
│   └── ...
└── script.py.mako
```

### Access Control

```sql
-- Create role for accounting module
CREATE ROLE accounting_app WITH LOGIN PASSWORD 'secure_password';
GRANT USAGE ON SCHEMA accounting TO accounting_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA accounting TO accounting_app;

-- Restrict cross-schema access
REVOKE ALL ON SCHEMA hr FROM accounting_app;
```

## Migration Strategy

### Phase 1: Schema Setup (Current)
- Create all schemas in existing database
- Migrate tables to appropriate schemas
- Update application connections

### Phase 2: Permission Hardening
- Implement schema-level roles
- Audit and restrict cross-schema access
- Document allowed cross-schema queries

### Phase 3: Extraction (When Needed)
Criteria for extraction to separate database:
- Schema exceeds 100GB
- Requires independent scaling
- Specific compliance requirements
- Performance isolation needed

Extraction process:
1. Set up new database instance
2. Use `pg_dump --schema` to extract
3. Update connection strings
4. Deploy with zero-downtime migration

## Alternatives Considered

### Option 1: Single Schema for All Tables
**Rejected because:**
- No logical separation
- Difficult to enforce boundaries
- Hard to extract later
- Security concerns with mixed data

### Option 2: Separate Databases from Start
**Rejected because:**
- Operational complexity too high initially
- Distributed transactions needed
- Increased infrastructure costs
- Overkill for current scale

### Option 3: Mixed Approach (Some Separate, Some Shared)
**Considered but rejected because:**
- Inconsistent patterns increase complexity
- Harder to maintain and document
- Schema separation provides consistent approach

## Governance

### Schema Changes
- New schemas require architectural review
- Schema migrations must be backward compatible
- Cross-schema foreign keys need approval

### Documentation Requirements
- Each schema must have README documenting:
  - Purpose and ownership
  - Key entities and relationships
  - Access patterns
  - Retention policies

### Monitoring Requirements
- Per-schema metrics:
  - Size growth
  - Query performance
  - Connection usage
  - Lock contention

## References

- [PostgreSQL Schema Documentation](https://www.postgresql.org/docs/current/ddl-schemas.html)
- [Schema-Based Multi-Tenancy Patterns](https://www.citusdata.com/blog/2018/06/28/three-multi-tenancy-patterns/)
- [Database Design for Microservices](https://www.oreilly.com/library/view/building-microservices/9781491950340/)

---

**Next Review Date**: 2024-07-15 or when any schema exceeds 50GB
