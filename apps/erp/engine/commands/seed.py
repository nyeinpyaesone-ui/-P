"""
ERP03 Database Seed Data Loader

Initializes the database with essential reference data for all ERP modules.
Safe to run multiple times (idempotent).
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def seed_database() -> bool:
    """
    Load seed data into the database.
    
    This function creates essential reference data required for the ERP system
    to function properly. It's idempotent and safe to run multiple times.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Import database connection
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Get database credentials from environment
        db_config = {
            "user": os.getenv("POSTGRES_USER", "erp"),
            "password": os.getenv("POSTGRES_PASSWORD", "erp_secure_password_change_me"),
            "host": os.getenv("POSTGRES_HOST", "postgres"),
            "port": int(os.getenv("POSTGRES_PORT", "5432")),
            "database": os.getenv("POSTGRES_DB", "erp_core"),
        }
        
        logger.info("Connecting to database for seed data...")
        conn = psycopg2.connect(**db_config, connect_timeout=10)
        conn.autocommit = False
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Seed accounting data
                _seed_accounting(cur)
                
                # Seed HR data
                _seed_hr(cur)
                
                # Seed inventory data
                _seed_inventory(cur)
                
                # Seed CRM data
                _seed_crm(cur)
                
                # Seed warehouse data
                _seed_warehouse(cur)
                
                logger.info("Seed data loaded successfully.")
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error loading seed data: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
            
    except ImportError:
        logger.warning("psycopg2 not available. Skipping seed data load.")
        return False
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def _seed_accounting(cur) -> None:
    """Seed accounting module reference data."""
    logger.info("Seeding accounting data...")
    
    # Create chart of accounts table if not exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS accounting.chart_of_accounts (
            id SERIAL PRIMARY KEY,
            account_code VARCHAR(20) UNIQUE NOT NULL,
            account_name VARCHAR(200) NOT NULL,
            account_type VARCHAR(50) NOT NULL,
            parent_account_id INTEGER REFERENCES accounting.chart_of_accounts(id),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Check if already seeded
    cur.execute("SELECT COUNT(*) FROM accounting.chart_of_accounts")
    if cur.fetchone()["count"] > 0:
        logger.info("Accounting data already exists. Skipping.")
        return
    
    # Insert default chart of accounts
    default_accounts = [
        ("1000", "Assets", "ASSET", None),
        ("1100", "Current Assets", "ASSET", "1000"),
        ("1110", "Cash", "ASSET", "1100"),
        ("1120", "Bank Accounts", "ASSET", "1100"),
        ("1200", "Accounts Receivable", "ASSET", "1100"),
        ("1300", "Inventory", "ASSET", "1100"),
        ("2000", "Liabilities", "LIABILITY", None),
        ("2100", "Current Liabilities", "LIABILITY", "2000"),
        ("2110", "Accounts Payable", "LIABILITY", "2100"),
        ("2200", "Long-term Debt", "LIABILITY", "2000"),
        ("3000", "Equity", "EQUITY", None),
        ("3100", "Owner's Equity", "EQUITY", "3000"),
        ("3200", "Retained Earnings", "EQUITY", "3000"),
        ("4000", "Revenue", "REVENUE", None),
        ("4100", "Sales Revenue", "REVENUE", "4000"),
        ("4200", "Service Revenue", "REVENUE", "4000"),
        ("5000", "Expenses", "EXPENSE", None),
        ("5100", "Cost of Goods Sold", "EXPENSE", "5000"),
        ("5200", "Operating Expenses", "EXPENSE", "5000"),
        ("5300", "Administrative Expenses", "EXPENSE", "5000"),
    ]
    
    for code, name, acc_type, parent_code in default_accounts:
        parent_id = None
        if parent_code:
            cur.execute("SELECT id FROM accounting.chart_of_accounts WHERE account_code = %s", (parent_code,))
            row = cur.fetchone()
            if row:
                parent_id = row["id"]
        
        cur.execute("""
            INSERT INTO accounting.chart_of_accounts (account_code, account_name, account_type, parent_account_id)
            VALUES (%s, %s, %s, %s)
        """, (code, name, acc_type, parent_id))


def _seed_hr(cur) -> None:
    """Seed HR module reference data."""
    logger.info("Seeding HR data...")
    
    # Create departments table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hr.departments (
            id SERIAL PRIMARY KEY,
            department_code VARCHAR(20) UNIQUE NOT NULL,
            department_name VARCHAR(200) NOT NULL,
            parent_department_id INTEGER REFERENCES hr.departments(id),
            manager_id INTEGER,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create employee statuses table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hr.employee_statuses (
            id SERIAL PRIMARY KEY,
            status_code VARCHAR(20) UNIQUE NOT NULL,
            status_name VARCHAR(100) NOT NULL,
            description TEXT
        );
    """)
    
    # Check if already seeded
    cur.execute("SELECT COUNT(*) FROM hr.departments")
    if cur.fetchone()["count"] > 0:
        logger.info("HR data already exists. Skipping.")
        return
    
    # Insert default departments
    departments = [
        ("EXEC", "Executive", None),
        ("FIN", "Finance", "EXEC"),
        ("HR", "Human Resources", "EXEC"),
        ("IT", "Information Technology", "EXEC"),
        ("OPS", "Operations", "EXEC"),
        ("SALES", "Sales", "OPS"),
        ("MKT", "Marketing", "OPS"),
        ("SUPPORT", "Customer Support", "OPS"),
    ]
    
    for code, name, parent_code in departments:
        parent_id = None
        if parent_code:
            cur.execute("SELECT id FROM hr.departments WHERE department_code = %s", (parent_code,))
            row = cur.fetchone()
            if row:
                parent_id = row["id"]
        
        cur.execute("""
            INSERT INTO hr.departments (department_code, department_name, parent_department_id)
            VALUES (%s, %s, %s)
        """, (code, name, parent_id))
    
    # Insert employee statuses
    statuses = [
        ("ACTIVE", "Active", "Currently employed"),
        ("PROBATION", "Probation", "Trial period"),
        ("LEAVE", "On Leave", "Temporary absence"),
        ("TERMINATED", "Terminated", "Employment ended"),
        ("RETIRED", "Retired", "Retired from company"),
    ]
    
    for code, name, desc in statuses:
        cur.execute("""
            INSERT INTO hr.employee_statuses (status_code, status_name, description)
            VALUES (%s, %s, %s)
        """, (code, name, desc))


def _seed_inventory(cur) -> None:
    """Seed inventory module reference data."""
    logger.info("Seeding inventory data...")
    
    # Create units of measure table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory.units_of_measure (
            id SERIAL PRIMARY KEY,
            uom_code VARCHAR(10) UNIQUE NOT NULL,
            uom_name VARCHAR(100) NOT NULL,
            uom_type VARCHAR(50) NOT NULL,
            description TEXT
        );
    """)
    
    # Create item categories table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory.item_categories (
            id SERIAL PRIMARY KEY,
            category_code VARCHAR(20) UNIQUE NOT NULL,
            category_name VARCHAR(200) NOT NULL,
            parent_category_id INTEGER REFERENCES inventory.item_categories(id),
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE
        );
    """)
    
    # Check if already seeded
    cur.execute("SELECT COUNT(*) FROM inventory.units_of_measure")
    if cur.fetchone()["count"] > 0:
        logger.info("Inventory data already exists. Skipping.")
        return
    
    # Insert units of measure
    uoms = [
        ("EA", "Each", "UNIT", "Individual item"),
        ("DOZ", "Dozen", "UNIT", "12 items"),
        ("BOX", "Box", "PACKAGE", "Standard box"),
        ("CASE", "Case", "PACKAGE", "Standard case"),
        ("PAL", "Pallet", "PACKAGE", "Standard pallet"),
        ("KG", "Kilogram", "WEIGHT", "Metric weight"),
        ("LB", "Pound", "WEIGHT", "Imperial weight"),
        ("L", "Liter", "VOLUME", "Metric volume"),
        ("GAL", "Gallon", "VOLUME", "Imperial volume"),
        ("M", "Meter", "LENGTH", "Metric length"),
        ("FT", "Foot", "LENGTH", "Imperial length"),
    ]
    
    for code, name, uom_type, desc in uoms:
        cur.execute("""
            INSERT INTO inventory.units_of_measure (uom_code, uom_name, uom_type, description)
            VALUES (%s, %s, %s, %s)
        """, (code, name, uom_type, desc))
    
    # Insert item categories
    categories = [
        ("RAW", "Raw Materials", None),
        ("WIP", "Work in Progress", None),
        ("FG", "Finished Goods", None),
        ("PACK", "Packaging", None),
        ("SUPPLY", "Supplies", None),
        ("SERVICE", "Services", None),
    ]
    
    for code, name, parent_code in categories:
        parent_id = None
        if parent_code:
            cur.execute("SELECT id FROM inventory.item_categories WHERE category_code = %s", (parent_code,))
            row = cur.fetchone()
            if row:
                parent_id = row["id"]
        
        cur.execute("""
            INSERT INTO inventory.item_categories (category_code, category_name, parent_category_id)
            VALUES (%s, %s, %s)
        """, (code, name, parent_id))


def _seed_crm(cur) -> None:
    """Seed CRM module reference data."""
    logger.info("Seeding CRM data...")
    
    # Create customer types table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS crm.customer_types (
            id SERIAL PRIMARY KEY,
            type_code VARCHAR(20) UNIQUE NOT NULL,
            type_name VARCHAR(100) NOT NULL,
            description TEXT
        );
    """)
    
    # Create customer statuses table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS crm.customer_statuses (
            id SERIAL PRIMARY KEY,
            status_code VARCHAR(20) UNIQUE NOT NULL,
            status_name VARCHAR(100) NOT NULL,
            description TEXT
        );
    """)
    
    # Create lead statuses table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS crm.lead_statuses (
            id SERIAL PRIMARY KEY,
            status_code VARCHAR(20) UNIQUE NOT NULL,
            status_name VARCHAR(100) NOT NULL,
            description TEXT,
            sort_order INTEGER DEFAULT 0
        );
    """)
    
    # Check if already seeded
    cur.execute("SELECT COUNT(*) FROM crm.customer_types")
    if cur.fetchone()["count"] > 0:
        logger.info("CRM data already exists. Skipping.")
        return
    
    # Insert customer types
    customer_types = [
        ("INDIVIDUAL", "Individual", "Single person customer"),
        ("BUSINESS", "Business", "Company or organization"),
        ("GOVERNMENT", "Government", "Government entity"),
        ("NONPROFIT", "Non-Profit", "Non-profit organization"),
        ("PARTNER", "Partner", "Business partner"),
    ]
    
    for code, name, desc in customer_types:
        cur.execute("""
            INSERT INTO crm.customer_types (type_code, type_name, description)
            VALUES (%s, %s, %s)
        """, (code, name, desc))
    
    # Insert customer statuses
    customer_statuses = [
        ("PROSPECT", "Prospect", "Potential customer"),
        ("ACTIVE", "Active", "Currently active customer"),
        ("INACTIVE", "Inactive", "Temporarily inactive"),
        ("CLOSED", "Closed", "Account closed"),
        ("BLACKLISTED", "Blacklisted", "Blocked customer"),
    ]
    
    for code, name, desc in customer_statuses:
        cur.execute("""
            INSERT INTO crm.customer_statuses (status_code, status_name, description)
            VALUES (%s, %s, %s)
        """, (code, name, desc))
    
    # Insert lead statuses
    lead_statuses = [
        ("NEW", "New Lead", "Recently captured lead", 1),
        ("CONTACTED", "Contacted", "Initial contact made", 2),
        ("QUALIFIED", "Qualified", "Lead qualified", 3),
        ("PROPOSAL", "Proposal Sent", "Proposal submitted", 4),
        ("NEGOTIATION", "Negotiation", "In negotiation", 5),
        ("WON", "Won", "Deal won", 6),
        ("LOST", "Lost", "Deal lost", 7),
    ]
    
    for code, name, desc, order in lead_statuses:
        cur.execute("""
            INSERT INTO crm.lead_statuses (status_code, status_name, description, sort_order)
            VALUES (%s, %s, %s, %s)
        """, (code, name, desc, order))


def _seed_warehouse(cur) -> None:
    """Seed warehouse module reference data."""
    logger.info("Seeding warehouse data...")
    
    # Create warehouse types table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS warehouse.warehouse_types (
            id SERIAL PRIMARY KEY,
            type_code VARCHAR(20) UNIQUE NOT NULL,
            type_name VARCHAR(100) NOT NULL,
            description TEXT
        );
    """)
    
    # Create location types table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS warehouse.location_types (
            id SERIAL PRIMARY KEY,
            type_code VARCHAR(20) UNIQUE NOT NULL,
            type_name VARCHAR(100) NOT NULL,
            description TEXT
        );
    """)
    
    # Check if already seeded
    cur.execute("SELECT COUNT(*) FROM warehouse.warehouse_types")
    if cur.fetchone()["count"] > 0:
        logger.info("Warehouse data already exists. Skipping.")
        return
    
    # Insert warehouse types
    warehouse_types = [
        ("MAIN", "Main Warehouse", "Primary storage facility"),
        ("REGIONAL", "Regional Warehouse", "Regional distribution center"),
        ("COLD", "Cold Storage", "Temperature-controlled storage"),
        ("HAZMAT", "Hazmat Storage", "Hazardous materials storage"),
        ("CROSSDOCK", "Cross-Dock", "Transfer facility"),
    ]
    
    for code, name, desc in warehouse_types:
        cur.execute("""
            INSERT INTO warehouse.warehouse_types (type_code, type_name, description)
            VALUES (%s, %s, %s)
        """, (code, name, desc))
    
    # Insert location types
    location_types = [
        ("RACK", "Rack", "Storage rack location"),
        ("SHELF", "Shelf", "Shelf location"),
        ("BIN", "Bin", "Bin location"),
        ("FLOOR", "Floor", "Floor storage area"),
        ("DOCK", "Dock", "Loading dock"),
        ("STAGING", "Staging", "Staging area"),
    ]
    
    for code, name, desc in location_types:
        cur.execute("""
            INSERT INTO warehouse.location_types (type_code, type_name, description)
            VALUES (%s, %s, %s)
        """, (code, name, desc))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = seed_database()
    exit(0 if success else 1)
