"""
ERP03 Database Models
Enterprise-grade SQLAlchemy models with audit trails and soft deletes.
"""
from datetime import datetime, timezone, date
from typing import Optional, List, Any
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, 
    Numeric, Text, Date, Enum as SQLEnum, Index, event
)
from sqlalchemy.orm import relationship, declarative_base, Mapped, mapped_column
import enum

Base = declarative_base()


# ============================================================================
# Base Audit Model - All ERP models inherit from this for compliance
# ============================================================================
class BaseAuditModel(Base):
    """Abstract base model with audit fields for GDPR/SOC2 compliance."""
    
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    created_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    def soft_delete(self, user_id: Optional[str] = None) -> None:
        """Mark record as deleted without removing from database."""
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
        self.deleted_by = user_id


# ============================================================================
# FINANCE & ACCOUNTING MODULE
# General Ledger, Accounts Payable/Receivable, Cash Management
# ============================================================================

class AccountType(enum.Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class Account(BaseAuditModel):
    """Chart of Accounts - Core GL structure."""
    
    __tablename__ = "accounts"
    __table_args__ = (Index('idx_account_code', 'account_code', unique=True),)
    
    account_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_type: Mapped[AccountType] = mapped_column(SQLEnum(AccountType), nullable=False)
    parent_account_id: Mapped[Optional[int]] = mapped_column(ForeignKey('accounts.id'), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    balance: Mapped[float] = mapped_column(Numeric(19, 4), default=0.00)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    parent_account: Mapped[Optional["Account"]] = relationship(
        "Account", remote_side=[id], backref="child_accounts"
    )
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="account")


class JournalEntry(BaseAuditModel):
    """Journal Entry Header for double-entry bookkeeping."""
    
    __tablename__ = "journal_entries"
    __table_args__ = (Index('idx_journal_date', 'entry_date'),)
    
    entry_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    posting_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    total_debit: Mapped[float] = mapped_column(Numeric(19, 4), default=0.00)
    total_credit: Mapped[float] = mapped_column(Numeric(19, 4), default=0.00)
    is_balanced: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    lines: Mapped[List["JournalEntryLine"]] = relationship(
        "JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan"
    )


class JournalEntryLine(BaseAuditModel):
    """Journal Entry Lines - Individual debit/credit entries."""
    
    __tablename__ = "journal_entry_lines"
    
    journal_entry_id: Mapped[int] = mapped_column(ForeignKey('journal_entries.id'), nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'), nullable=False)
    line_description: Mapped[str] = mapped_column(String(255), nullable=True)
    debit_amount: Mapped[float] = mapped_column(Numeric(19, 4), default=0.00)
    credit_amount: Mapped[float] = mapped_column(Numeric(19, 4), default=0.00)
    
    # Relationships
    journal_entry: Mapped["JournalEntry"] = relationship("JournalEntry", back_populates="lines")
    account: Mapped["Account"] = relationship("Account", back_populates="transactions")


class Transaction(BaseAuditModel):
    """Financial Transactions - Links to GL accounts."""
    
    __tablename__ = "transactions"
    __table_args__ = (Index('idx_transaction_date', 'transaction_date'),)
    
    transaction_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(19, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    account: Mapped["Account"] = relationship("Account", back_populates="transactions")


class Supplier(BaseAuditModel):
    """Accounts Payable - Suppliers/Vendors."""
    
    __tablename__ = "suppliers"
    
    supplier_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    supplier_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tax_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    payment_terms_days: Mapped[int] = mapped_column(Integer, default=30)
    outstanding_balance: Mapped[float] = mapped_column(Numeric(19, 4), default=0.00)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Customer(BaseAuditModel):
    """Accounts Receivable - Customers."""
    
    __tablename__ = "customers"
    
    customer_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tax_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    credit_limit: Mapped[float] = mapped_column(Numeric(19, 4), default=0.00)
    outstanding_balance: Mapped[float] = mapped_column(Numeric(19, 4), default=0.00)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class CashFlow(BaseAuditModel):
    """Cash Management - Cash flow tracking."""
    
    __tablename__ = "cash_flows"
    
    cash_flow_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(19, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    flow_type: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


# ============================================================================
# HUMAN CAPITAL MANAGEMENT (HCM) MODULE
# Payroll, Employee Lifecycle, Performance Management
# ============================================================================

class EmployeeStatus(enum.Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"
    RETIRED = "retired"


class Employee(BaseAuditModel):
    """Employee Records - Core HCM structure."""
    
    __tablename__ = "employees"
    __table_args__ = (Index('idx_employee_code', 'employee_code', unique=True),)
    
    employee_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    termination_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    job_title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey('departments.id'), nullable=True)
    manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey('employees.id'), nullable=True)
    status: Mapped[EmployeeStatus] = mapped_column(SQLEnum(EmployeeStatus), default=EmployeeStatus.ACTIVE)
    salary: Mapped[Optional[float]] = mapped_column(Numeric(19, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    # Relationships
    department: Mapped[Optional["Department"]] = relationship("Department", back_populates="employees")
    manager: Mapped[Optional["Employee"]] = relationship(
        "Employee", remote_side=[id], backref="subordinates"
    )
    payroll_records: Mapped[List["Payroll"]] = relationship("Payroll", back_populates="employee")


class Department(BaseAuditModel):
    """Organizational Departments."""
    
    __tablename__ = "departments"
    
    department_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    department_name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_department_id: Mapped[Optional[int]] = mapped_column(ForeignKey('departments.id'), nullable=True)
    cost_center: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    parent_department: Mapped[Optional["Department"]] = relationship(
        "Department", remote_side=[id], backref="child_departments"
    )
    employees: Mapped[List["Employee"]] = relationship("Employee", back_populates="department")


class Payroll(BaseAuditModel):
    """Payroll Processing - Salary payments and deductions."""
    
    __tablename__ = "payroll"
    
    payroll_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey('employees.id'), nullable=False)
    pay_period_start: Mapped[date] = mapped_column(Date, nullable=False)
    pay_period_end: Mapped[date] = mapped_column(Date, nullable=False)
    pay_date: Mapped[date] = mapped_column(Date, nullable=False)
    gross_salary: Mapped[float] = mapped_column(Numeric(19, 2), nullable=False)
    net_salary: Mapped[float] = mapped_column(Numeric(19, 2), nullable=False)
    tax_deduction: Mapped[float] = mapped_column(Numeric(19, 2), default=0.00)
    other_deductions: Mapped[float] = mapped_column(Numeric(19, 2), default=0.00)
    bonuses: Mapped[float] = mapped_column(Numeric(19, 2), default=0.00)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="payroll_records")


class PerformanceReview(BaseAuditModel):
    """Employee Performance Reviews."""
    
    __tablename__ = "performance_reviews"
    
    employee_id: Mapped[int] = mapped_column(ForeignKey('employees.id'), nullable=False)
    reviewer_id: Mapped[Optional[int]] = mapped_column(ForeignKey('employees.id'), nullable=True)
    review_date: Mapped[date] = mapped_column(Date, nullable=False)
    review_period_start: Mapped[date] = mapped_column(Date, nullable=False)
    review_period_end: Mapped[date] = mapped_column(Date, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=True)
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    goals: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    
    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[employee_id])
    reviewer: Mapped[Optional["Employee"]] = relationship("Employee", foreign_keys=[reviewer_id])


# ============================================================================
# SUPPLY CHAIN MANAGEMENT (SCM) MODULE
# Inventory Tracking, Procurement, Logistics, Order Management
# ============================================================================

class Product(BaseAuditModel):
    """Product Master Data."""
    
    __tablename__ = "products"
    __table_args__ = (Index('idx_product_sku', 'sku', unique=True),)
    
    product_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    sku: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    unit_of_measure: Mapped[str] = mapped_column(String(20), default="unit", nullable=False)
    standard_cost: Mapped[float] = mapped_column(Numeric(19, 4), default=0.00)
    selling_price: Mapped[float] = mapped_column(Numeric(19, 4), default=0.00)
    reorder_level: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    stock_levels: Mapped[List["StockLevel"]] = relationship("StockLevel", back_populates="product")
    order_items: Mapped[List["SalesOrderItem"]] = relationship("SalesOrderItem", back_populates="product")


class StockLevel(BaseAuditModel):
    """Inventory Stock Levels by Warehouse."""
    
    __tablename__ = "stock_levels"
    __table_args__ = (Index('idx_stock_product_warehouse', 'product_id', 'warehouse_id', unique=True),)
    
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey('warehouses.id'), nullable=False)
    quantity_on_hand: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    quantity_reserved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    quantity_available: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reorder_point: Mapped[int] = mapped_column(Integer, default=0)
    last_counted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="stock_levels")
    warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates="stock_levels")


class Warehouse(BaseAuditModel):
    """Warehouse Locations."""
    
    __tablename__ = "warehouses"
    
    warehouse_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    warehouse_name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    stock_levels: Mapped[List["StockLevel"]] = relationship("StockLevel", back_populates="warehouse")
    shipments: Mapped[List["Shipment"]] = relationship("Shipment", back_populates="warehouse")


class PurchaseOrder(BaseAuditModel):
    """Procurement - Purchase Orders."""
    
    __tablename__ = "purchase_orders"
    
    po_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey('suppliers.id'), nullable=False)
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_delivery_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_delivery_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    total_amount: Mapped[float] = mapped_column(Numeric(19, 4), default=0.00)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    supplier: Mapped["Supplier"] = relationship("Supplier")


class SalesOrder(BaseAuditModel):
    """Sales - Customer Orders."""
    
    __tablename__ = "sales_orders"
    
    order_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'), nullable=False)
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    required_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    shipped_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    total_amount: Mapped[float] = mapped_column(Numeric(19, 4), default=0.00)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    shipping_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    customer: Mapped["Customer"] = relationship("Customer")
    order_items: Mapped[List["SalesOrderItem"]] = relationship(
        "SalesOrderItem", back_populates="sales_order", cascade="all, delete-orphan"
    )


class SalesOrderItem(BaseAuditModel):
    """Sales Order Line Items."""
    
    __tablename__ = "sales_order_items"
    
    sales_order_id: Mapped[int] = mapped_column(ForeignKey('sales_orders.id'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(19, 4), nullable=False)
    discount_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00)
    line_total: Mapped[float] = mapped_column(Numeric(19, 4), nullable=False)
    
    # Relationships
    sales_order: Mapped["SalesOrder"] = relationship("SalesOrder", back_populates="order_items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")


class Shipment(BaseAuditModel):
    """Logistics - Shipments Tracking."""
    
    __tablename__ = "shipments"
    
    shipment_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    sales_order_id: Mapped[Optional[int]] = mapped_column(ForeignKey('sales_orders.id'), nullable=True)
    purchase_order_id: Mapped[Optional[int]] = mapped_column(ForeignKey('purchase_orders.id'), nullable=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey('warehouses.id'), nullable=False)
    shipment_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    delivery_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    carrier: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tracking_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    shipping_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates="shipments")
    sales_order: Mapped[Optional["SalesOrder"]] = relationship("SalesOrder")
    purchase_order: Mapped[Optional["PurchaseOrder"]] = relationship("PurchaseOrder")


# ============================================================================
# MANUFACTURING / MRP MODULE
# Production Scheduling, Bill of Materials, Quality Control
# ============================================================================

class BillOfMaterial(BaseAuditModel):
    """Bill of Materials (BOM) - Product recipes."""
    
    __tablename__ = "bill_of_materials"
    
    bom_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)
    version: Mapped[str] = mapped_column(String(20), default="1.0", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    product: Mapped["Product"] = relationship("Product", foreign_keys=[product_id])
    bom_items: Mapped[List["BOMItem"]] = relationship(
        "BOMItem", back_populates="bom", cascade="all, delete-orphan"
    )


class BOMItem(BaseAuditModel):
    """Bill of Material Line Items."""
    
    __tablename__ = "bom_items"
    
    bom_id: Mapped[int] = mapped_column(ForeignKey('bill_of_materials.id'), nullable=False)
    component_product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(19, 4), nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(String(20), default="unit", nullable=False)
    scrap_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00)
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    bom: Mapped["BillOfMaterial"] = relationship("BillOfMaterial", back_populates="bom_items")
    component_product: Mapped["Product"] = relationship("Product", foreign_keys=[component_product_id])


class ProductionOrder(BaseAuditModel):
    """Production Orders - Manufacturing jobs."""
    
    __tablename__ = "production_orders"
    
    production_order_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)
    bom_id: Mapped[Optional[int]] = mapped_column(ForeignKey('bill_of_materials.id'), nullable=True)
    quantity_to_produce: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_produced: Mapped[int] = mapped_column(Integer, default=0)
    planned_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    planned_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="planned")
    priority: Mapped[str] = mapped_column(String(20), default="normal")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    product: Mapped["Product"] = relationship("Product", foreign_keys=[product_id])
    bom: Mapped[Optional["BillOfMaterial"]] = relationship("BillOfMaterial")


class QualityInspection(BaseAuditModel):
    """Quality Control - Inspection records."""
    
    __tablename__ = "quality_inspections"
    
    inspection_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    production_order_id: Mapped[Optional[int]] = mapped_column(ForeignKey('production_orders.id'), nullable=True)
    purchase_order_id: Mapped[Optional[int]] = mapped_column(ForeignKey('purchase_orders.id'), nullable=True)
    inspection_date: Mapped[date] = mapped_column(Date, nullable=False)
    inspector_id: Mapped[Optional[int]] = mapped_column(ForeignKey('employees.id'), nullable=True)
    inspection_type: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity_inspected: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_passed: Mapped[int] = mapped_column(Integer, default=0)
    quantity_failed: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    defect_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    corrective_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    production_order: Mapped[Optional["ProductionOrder"]] = relationship("ProductionOrder")
    purchase_order: Mapped[Optional["PurchaseOrder"]] = relationship("PurchaseOrder")
    inspector: Mapped[Optional["Employee"]] = relationship("Employee")


# ============================================================================
# CUSTOMER RELATIONSHIP MANAGEMENT (CRM) MODULE
# Sales Pipelines, Customer History, Support Tickets
# ============================================================================

class Lead(BaseAuditModel):
    """CRM Leads - Potential customers."""
    
    __tablename__ = "leads"
    
    lead_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    lead_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    estimated_value: Mapped[Optional[float]] = mapped_column(Numeric(19, 2), nullable=True)
    probability: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="new")
    assigned_to_id: Mapped[Optional[int]] = mapped_column(ForeignKey('employees.id'), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    assigned_to: Mapped[Optional["Employee"]] = relationship("Employee")


class Opportunity(BaseAuditModel):
    """CRM Opportunities - Active sales deals."""
    
    __tablename__ = "opportunities"
    
    opportunity_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey('customers.id'), nullable=True)
    opportunity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    stage: Mapped[str] = mapped_column(String(50), default="prospecting")
    estimated_value: Mapped[float] = mapped_column(Numeric(19, 2), nullable=False)
    probability: Mapped[int] = mapped_column(Integer, default=0)
    expected_close_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_close_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    assigned_to_id: Mapped[Optional[int]] = mapped_column(ForeignKey('employees.id'), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    customer: Mapped[Optional["Customer"]] = relationship("Customer")
    assigned_to: Mapped[Optional["Employee"]] = relationship("Employee")


class SupportTicket(BaseAuditModel):
    """CRM Support Tickets - Customer service requests."""
    
    __tablename__ = "support_tickets"
    
    ticket_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(20), default="open")
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    assigned_to_id: Mapped[Optional[int]] = mapped_column(ForeignKey('employees.id'), nullable=True)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    customer: Mapped["Customer"] = relationship("Customer")
    assigned_to: Mapped[Optional["Employee"]] = relationship("Employee")


class Interaction(BaseAuditModel):
    """CRM Interactions - Customer communication history."""
    
    __tablename__ = "interactions"
    
    interaction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey('customers.id'), nullable=True)
    lead_id: Mapped[Optional[int]] = mapped_column(ForeignKey('leads.id'), nullable=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey('employees.id'), nullable=False)
    interaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    follow_up_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Relationships
    customer: Mapped[Optional["Customer"]] = relationship("Customer")
    lead: Mapped[Optional["Lead"]] = relationship("Lead")
    employee: Mapped["Employee"] = relationship("Employee")


# ============================================================================
# REPORTING & ANALYTICS MODULE
# Business Intelligence, KPI Tracking, Compliance Reports
# ============================================================================

class ReportDefinition(BaseAuditModel):
    """Report Definitions - Configurable report templates."""
    
    __tablename__ = "report_definitions"
    
    report_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    report_name: Mapped[str] = mapped_column(String(255), nullable=False)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    module: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    query_sql: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parameters: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    report_executions: Mapped[List["ReportExecution"]] = relationship(
        "ReportExecution", back_populates="report_definition"
    )


class ReportExecution(BaseAuditModel):
    """Report Execution History - Audit trail of report runs."""
    
    __tablename__ = "report_executions"
    
    report_definition_id: Mapped[int] = mapped_column(ForeignKey('report_definitions.id'), nullable=False)
    executed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    execution_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    parameters_used: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rows_returned: Mapped[int] = mapped_column(Integer, default=0)
    execution_time_ms: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="success")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    output_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Relationships
    report_definition: Mapped["ReportDefinition"] = relationship("ReportDefinition", back_populates="report_executions")


class KPIMetric(BaseAuditModel):
    """KPI Metrics - Key Performance Indicators tracking."""
    
    __tablename__ = "kpi_metrics"
    
    metric_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    target_value: Mapped[float] = mapped_column(Numeric(19, 4), nullable=False)
    current_value: Mapped[float] = mapped_column(Numeric(19, 4), default=0.00)
    unit_of_measure: Mapped[str] = mapped_column(String(50), nullable=False)
    calculation_method: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    update_frequency: Mapped[str] = mapped_column(String(20), default="daily")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    metric_history: Mapped[List["KPIMetricHistory"]] = relationship(
        "KPIMetricHistory", back_populates="kpi_metric", cascade="all, delete-orphan"
    )


class KPIMetricHistory(BaseAuditModel):
    """KPI Metric History - Historical values for trending."""
    
    __tablename__ = "kpi_metric_history"
    
    kpi_metric_id: Mapped[int] = mapped_column(ForeignKey('kpi_metrics.id'), nullable=False)
    measurement_date: Mapped[date] = mapped_column(Date, nullable=False)
    measured_value: Mapped[float] = mapped_column(Numeric(19, 4), nullable=False)
    target_value: Mapped[float] = mapped_column(Numeric(19, 4), nullable=False)
    variance: Mapped[float] = mapped_column(Numeric(19, 4), default=0.00)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    kpi_metric: Mapped["KPIMetric"] = relationship("KPIMetric", back_populates="metric_history")


# ============================================================================
# Event-Driven Architecture Support
# For RabbitMQ/Celery async workflows
# ============================================================================

class DomainEvent(BaseAuditModel):
    """Domain Events - Event sourcing for async integration."""
    
    __tablename__ = "domain_events"
    __table_args__ = (Index('idx_event_type', 'event_type'),)
    
    event_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String(100), nullable=False)
    aggregate_id: Mapped[int] = mapped_column(Integer, nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    def mark_published(self) -> None:
        """Mark event as published."""
        self.published = True
        self.published_at = datetime.now(timezone.utc)
