# Alembic Migration Configuration

ERP03 Database Migrations using Alembic

## Setup

Alembic is configured to work with multiple PostgreSQL schemas. Each business domain has its own migration stream.

## Directory Structure

```
migrations/
├── versions/           # Migration scripts
│   ├── accounting_001_initial.py
│   ├── sales_001_initial.py
│   └── ...
├── env.py             # Migration environment
├── script.py.mako     # Template for new migrations
└── README.md          # This file
```

## Configuration

### alembic.ini

Key configuration options:

```ini
[alembic]
script_location = migrations
prepend_sys_path = .
sqlalchemy.url = postgresql://user:pass@host:5432/erp_core

[post_write_hooks]
hooks = black
black.type = console_scripts
black.entrypoint = black
black.options = -q
```

## Usage

### Generate New Migration

```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "Add journal_entries table"

# Create empty migration
alembic revision -m "Create initial accounting schema"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade <revision_id>

# Downgrade one version
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade <revision_id>
```

### Check Status

```bash
# Show current revision
alembic current

# Show pending migrations
alembic history

# Show full history
alembic history -v
```

## Schema-Specific Migrations

Each schema has independent migration tracking:

### Accounting Schema

```bash
# Set search path to accounting
export ALEMBIC_CONFIG_OPTIONS="-c search_path=accounting"

# Run migrations for accounting only
alembic upgrade head --opt "$ALEMBIC_CONFIG_OPTIONS"
```

### Multiple Schemas

For multi-schema migrations, use the `--schema` flag in migration scripts:

```python
def upgrade():
    op.create_table(
        'journal_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        schema='accounting'
    )
```

## Migration Script Template

```python
"""Add journal_entries table

Revision ID: abc123
Revises: def456
Create Date: 2024-01-15 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123'
down_revision = 'def456'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'journal_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('debit', sa.Numeric(19, 4), nullable=False),
        sa.Column('credit', sa.Numeric(19, 4), nullable=False),
        sa.Column('description', sa.String(500)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        schema='accounting'
    )
    
    op.create_index(
        'ix_journal_entries_account_id',
        'journal_entries',
        ['account_id'],
        schema='accounting'
    )


def downgrade():
    op.drop_index(
        'ix_journal_entries_account_id',
        table_name='journal_entries',
        schema='accounting'
    )
    
    op.drop_table(
        'journal_entries',
        schema='accounting'
    )
```

## Best Practices

### 1. Schema Qualification

Always specify schema in migrations:

```python
# Good
op.create_table('users', ..., schema='hr')

# Bad - uses default search_path
op.create_table('users', ...)
```

### 2. Backward Compatibility

- Never modify existing columns in ways that break existing code
- Use `server_default` for new required columns
- Add new columns as nullable first, then backfill, then make required

### 3. Data Migrations

Separate schema changes from data migrations:

```python
def upgrade():
    # Step 1: Add column as nullable
    op.add_column('accounts', sa.Column('new_field', sa.String()), schema='sales')
    
    # Step 2: Backfill data (in separate transaction or script)
    # Run backfill script here or separately
    
    # Step 3: Make column required (in next migration)
    op.alter_column('accounts', 'new_field', nullable=False, schema='sales')
```

### 4. Index Creation

Create indexes concurrently in production to avoid locks:

```python
def upgrade():
    # For production, use concurrent=True
    op.create_index(
        'ix_accounts_name',
        'accounts',
        ['name'],
        schema='accounting',
        postgresql_concurrently=True
    )
```

Note: `postgresql_concurrently` cannot be used in a transaction block.

### 5. Rollback Safety

Always test downgrades:

```bash
# Test downgrade and upgrade
alembic downgrade -1
alembic upgrade head
```

## Common Operations

### Add Column

```python
def upgrade():
    op.add_column(
        'accounts',
        sa.Column('description', sa.String(500), nullable=True),
        schema='accounting'
    )

def downgrade():
    op.drop_column('accounts', 'description', schema='accounting')
```

### Modify Column

```python
def upgrade():
    op.alter_column(
        'accounts',
        'name',
        existing_type=sa.String(100),
        type_=sa.String(200),
        schema='accounting'
    )

def downgrade():
    op.alter_column(
        'accounts',
        'name',
        existing_type=sa.String(200),
        type_=sa.String(100),
        schema='accounting'
    )
```

### Create Index

```python
def upgrade():
    op.create_index(
        'ix_accounts_created_at',
        'accounts',
        ['created_at'],
        schema='accounting'
    )

def downgrade():
    op.drop_index(
        'ix_accounts_created_at',
        table_name='accounts',
        schema='accounting'
    )
```

### Create Foreign Key

```python
def upgrade():
    op.create_foreign_key(
        'fk_journal_account',
        'journal_entries',
        'accounts',
        ['account_id'],
        ['id'],
        source_schema='accounting',
        referent_schema='accounting'
    )
```

## Troubleshooting

### Migration Fails with Lock Timeout

For large tables, run during low-traffic periods or use concurrent operations:

```python
op.create_index(..., postgresql_concurrently=True)
```

### Head Detection Error

If you get "Multiple heads" error:

```bash
# See all heads
alembic heads

# Merge heads
alembic merge -r <head1> <head2> -m "Merge heads"
```

### Stamp Current State

If database already has tables:

```bash
# Stamp current state without running migrations
alembic stamp head
```

## Integration with CI/CD

Migrations run automatically in deployment pipeline:

```yaml
# .github/workflows/deploy.yml
- name: Run database migrations
  run: |
    alembic upgrade head
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

## References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Schema Documentation](https://www.postgresql.org/docs/current/ddl-schemas.html)
- [Schema Migrations Best Practices](https://martinfowler.com/articles/schema-migration.html)
