"""SCM Models - Supply Chain Management: Products, Inventory, Orders"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text, Date, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, date
from typing import Optional, List
from apps.erp.framework.database.models import Base, BaseAuditModel


class Product(BaseAuditModel):
    """Product Master Data."""
    
    __tablename__ = "scm_products"
    
    product_code = Column(String(50), unique=True, nullable=False)
    sku = Column(String(100), unique=True, nullable=False)
    product_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    unit_of_measure = Column(String(20), default="unit", nullable=False)
    standard_cost = Column(Numeric(19, 4), default=0.00)
    selling_price = Column(Numeric(19, 4), default=0.00)
    reorder_level = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)


class Warehouse(BaseAuditModel):
    """Warehouse Locations."""
    
    __tablename__ = "scm_warehouses"
    
    warehouse_code = Column(String(50), unique=True, nullable=False)
    warehouse_name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)


class StockLevel(BaseAuditModel):
    """Inventory Stock Levels by Warehouse."""
    
    __tablename__ = "scm_stock_levels"
    
    product_id = Column(Integer, ForeignKey("scm_products.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("scm_warehouses.id"), nullable=False)
    quantity_on_hand = Column(Integer, default=0, nullable=False)
    quantity_reserved = Column(Integer, default=0, nullable=False)
    quantity_available = Column(Integer, default=0, nullable=False)
    reorder_point = Column(Integer, default=0)
    last_counted_at = Column(DateTime(timezone=True), nullable=True)


class PurchaseOrderStatus:
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class PurchaseOrder(BaseAuditModel):
    """Procurement - Purchase Orders."""
    
    __tablename__ = "scm_purchase_orders"
    
    po_number = Column(String(50), unique=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    order_date = Column(Date, nullable=False)
    expected_delivery_date = Column(Date, nullable=True)
    actual_delivery_date = Column(Date, nullable=True)
    status = Column(String(20), default=PurchaseOrderStatus.DRAFT)
    total_amount = Column(Numeric(19, 4), default=0.00)
    currency = Column(String(3), default="USD")
    notes = Column(Text, nullable=True)


class SalesOrderStatus:
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class SalesOrder(BaseAuditModel):
    """Sales - Customer Orders."""
    
    __tablename__ = "scm_sales_orders"
    
    order_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    order_date = Column(Date, nullable=False)
    required_date = Column(Date, nullable=True)
    shipped_date = Column(Date, nullable=True)
    status = Column(String(20), default=SalesOrderStatus.PENDING)
    total_amount = Column(Numeric(19, 4), default=0.00)
    currency = Column(String(3), default="USD")
    shipping_address = Column(Text, nullable=True)


class SalesOrderItem(BaseAuditModel):
    """Sales Order Line Items."""
    
    __tablename__ = "scm_sales_order_items"
    
    sales_order_id = Column(Integer, ForeignKey("scm_sales_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("scm_products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(19, 4), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0.00)
    line_total = Column(Numeric(19, 4), nullable=False)
