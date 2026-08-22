-- ERP03 Database Initialization Script
-- Creates required schemas for all ERP modules

-- Accounting Schema
CREATE SCHEMA IF NOT EXISTS accounting;
COMMENT ON SCHEMA accounting IS 'Financial accounting and general ledger';

-- Sales Schema
CREATE SCHEMA IF NOT EXISTS sales;
COMMENT ON SCHEMA sales IS 'Sales orders, invoices, and customer management';

-- Inventory Schema
CREATE SCHEMA IF NOT EXISTS inventory;
COMMENT ON SCHEMA inventory IS 'Inventory tracking and stock management';

-- HR Schema
CREATE SCHEMA IF NOT EXISTS hr;
COMMENT ON SCHEMA hr IS 'Human resources and employee management';

-- CRM Schema
CREATE SCHEMA IF NOT EXISTS crm;
COMMENT ON SCHEMA crm IS 'Customer relationship management';

-- Warehouse Schema
CREATE SCHEMA IF NOT EXISTS warehouse;
COMMENT ON SCHEMA warehouse IS 'Warehouse operations and logistics';

-- Logistics Schema
CREATE SCHEMA IF NOT EXISTS logistics;
COMMENT ON SCHEMA logistics IS 'Supply chain and transportation management';

-- Reporting Schema
CREATE SCHEMA IF NOT EXISTS reporting;
COMMENT ON SCHEMA reporting IS 'Analytics and business intelligence';

-- Grant permissions to ERP user
DO $$
DECLARE
    schema_name text;
BEGIN
    FOR schema_name IN 
        SELECT nspname FROM pg_namespace 
        WHERE nspname IN ('accounting', 'sales', 'inventory', 'hr', 'crm', 'warehouse', 'logistics', 'reporting')
    LOOP
        EXECUTE format('GRANT ALL PRIVILEGES ON SCHEMA %I TO %I', schema_name, current_setting('POSTGRES_USER'));
    END LOOP;
END $$;

-- Create extension for UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create extension for JSON operations
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'ERP03 database schemas created successfully';
END $$;
