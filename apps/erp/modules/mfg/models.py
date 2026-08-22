"""MFG Models - Manufacturing: BOM, Production Orders, Quality Control"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text, Date, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, date
from typing import Optional, List
from apps.erp.framework.database.models import Base, BaseAuditModel


class BillOfMaterial(BaseAuditModel):
    """Bill of Materials (BOM) - Product recipes."""
    
    __tablename__ = "mfg_bill_of_materials"
    
    bom_number = Column(String(50), unique=True, nullable=False)
    product_id = Column(Integer, ForeignKey("scm_products.id"), nullable=False)
    version = Column(String(20), default="1.0", nullable=False)
    is_active = Column(Boolean, default=True)
    effective_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)


class BOMItem(BaseAuditModel):
    """Bill of Material Line Items."""
    
    __tablename__ = "mfg_bom_items"
    
    bom_id = Column(Integer, ForeignKey("mfg_bill_of_materials.id"), nullable=False)
    component_product_id = Column(Integer, ForeignKey("scm_products.id"), nullable=False)
    quantity = Column(Numeric(19, 4), nullable=False)
    unit_of_measure = Column(String(20), default="unit", nullable=False)
    scrap_percent = Column(Numeric(5, 2), default=0.00)
    sequence = Column(Integer, default=0)


class ProductionOrderStatus:
    PLANNED = "planned"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProductionOrderPriority:
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ProductionOrder(BaseAuditModel):
    """Production Orders - Manufacturing jobs."""
    
    __tablename__ = "mfg_production_orders"
    
    production_order_number = Column(String(50), unique=True, nullable=False)
    product_id = Column(Integer, ForeignKey("scm_products.id"), nullable=False)
    bom_id = Column(Integer, ForeignKey("mfg_bill_of_materials.id"), nullable=True)
    quantity_to_produce = Column(Integer, nullable=False)
    quantity_produced = Column(Integer, default=0)
    planned_start_date = Column(Date, nullable=False)
    planned_end_date = Column(Date, nullable=False)
    actual_start_date = Column(Date, nullable=True)
    actual_end_date = Column(Date, nullable=True)
    status = Column(String(20), default=ProductionOrderStatus.PLANNED)
    priority = Column(String(20), default=ProductionOrderPriority.NORMAL)
    notes = Column(Text, nullable=True)


class QualityInspectionStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    HOLD = "hold"


class QualityInspection(BaseAuditModel):
    """Quality Control - Inspection records."""
    
    __tablename__ = "mfg_quality_inspections"
    
    inspection_number = Column(String(50), unique=True, nullable=False)
    production_order_id = Column(Integer, ForeignKey("mfg_production_orders.id"), nullable=True)
    purchase_order_id = Column(Integer, ForeignKey("scm_purchase_orders.id"), nullable=True)
    inspection_date = Column(Date, nullable=False)
    inspector_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    inspection_type = Column(String(50), nullable=False)
    quantity_inspected = Column(Integer, nullable=False)
    quantity_passed = Column(Integer, default=0)
    quantity_failed = Column(Integer, default=0)
    status = Column(String(20), default=QualityInspectionStatus.PENDING)
    defect_description = Column(Text, nullable=True)
    corrective_action = Column(Text, nullable=True)
