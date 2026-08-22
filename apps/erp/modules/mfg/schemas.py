"""MFG Schemas - Pydantic Models for Manufacturing API"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


# ============================================================================
# Bill of Material Schemas
# ============================================================================

class BOMItemBase(BaseModel):
    """Base schema for BOM Item."""
    component_product_id: int
    quantity: float = Field(..., gt=0)
    unit_of_measure: str = Field(default="unit", max_length=20)
    scrap_percent: float = Field(default=0.0, ge=0, le=100)
    sequence: int = Field(default=0, ge=0)


class BOMItemCreate(BOMItemBase):
    """Schema for creating a BOM Item."""
    pass


class BOMItemResponse(BOMItemBase):
    """Schema for BOM Item response."""
    id: int
    bom_id: int
    
    class Config:
        from_attributes = True


class BillOfMaterialBase(BaseModel):
    """Base schema for Bill of Material."""
    product_id: int
    version: str = Field(default="1.0", max_length=20)
    effective_date: date
    expiry_date: Optional[date] = None
    notes: Optional[str] = None
    is_active: bool = True


class BillOfMaterialCreate(BillOfMaterialBase):
    """Schema for creating a Bill of Material."""
    items: List[BOMItemCreate] = []


class BillOfMaterialResponse(BillOfMaterialBase):
    """Schema for Bill of Material response."""
    id: int
    bom_number: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Production Order Schemas
# ============================================================================

class ProductionOrderBase(BaseModel):
    """Base schema for Production Order."""
    product_id: int
    bom_id: Optional[int] = None
    quantity_to_produce: int = Field(..., gt=0)
    planned_start_date: date
    planned_end_date: date
    priority: str = Field(default="normal", max_length=20)
    notes: Optional[str] = None


class ProductionOrderCreate(ProductionOrderBase):
    """Schema for creating a Production Order."""
    pass


class ProductionOrderResponse(ProductionOrderBase):
    """Schema for Production Order response."""
    id: int
    production_order_number: str
    status: str
    quantity_produced: int = 0
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Quality Inspection Schemas
# ============================================================================

class QualityInspectionBase(BaseModel):
    """Base schema for Quality Inspection."""
    inspection_type: str = Field(..., max_length=50)
    inspection_date: date
    production_order_id: Optional[int] = None
    purchase_order_id: Optional[int] = None
    inspector_id: Optional[int] = None
    quantity_inspected: int = Field(..., gt=0)
    defect_description: Optional[str] = None
    corrective_action: Optional[str] = None


class QualityInspectionCreate(QualityInspectionBase):
    """Schema for creating a Quality Inspection."""
    pass


class QualityInspectionResponse(QualityInspectionBase):
    """Schema for Quality Inspection response."""
    id: int
    inspection_number: str
    status: str
    quantity_passed: int = 0
    quantity_failed: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True
