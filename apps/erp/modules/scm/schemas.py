"""SCM Schemas - Pydantic Models for Supply Chain Management API"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import date, datetime


# ============================================================================
# Product Schemas
# ============================================================================

class ProductBase(BaseModel):
    """Base schema for Product."""
    product_name: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    unit_of_measure: str = Field(default="unit", max_length=20)
    standard_cost: float = Field(default=0.0, ge=0)
    selling_price: float = Field(default=0.0, ge=0)
    reorder_level: int = Field(default=0, ge=0)
    is_active: bool = True


class ProductCreate(ProductBase):
    """Schema for creating a Product."""
    pass


class ProductResponse(ProductBase):
    """Schema for Product response."""
    id: int
    product_code: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Warehouse Schemas
# ============================================================================

class WarehouseBase(BaseModel):
    """Base schema for Warehouse."""
    warehouse_name: str = Field(..., min_length=1, max_length=255)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: str = Field(..., max_length=100)
    is_active: bool = True


class WarehouseCreate(WarehouseBase):
    """Schema for creating a Warehouse."""
    pass


class WarehouseResponse(WarehouseBase):
    """Schema for Warehouse response."""
    id: int
    warehouse_code: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Stock Level Schemas
# ============================================================================

class StockLevelResponse(BaseModel):
    """Schema for Stock Level response."""
    id: int
    product_id: int
    warehouse_id: int
    quantity_on_hand: int
    quantity_reserved: int
    quantity_available: int
    reorder_point: int
    last_counted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Purchase Order Schemas
# ============================================================================

class PurchaseOrderBase(BaseModel):
    """Base schema for Purchase Order."""
    supplier_id: int
    order_date: date
    expected_delivery_date: Optional[date] = None
    notes: Optional[str] = None
    currency: str = Field(default="USD", max_length=3)


class PurchaseOrderCreate(PurchaseOrderBase):
    """Schema for creating a Purchase Order."""
    pass


class PurchaseOrderResponse(PurchaseOrderBase):
    """Schema for Purchase Order response."""
    id: int
    po_number: str
    status: str
    total_amount: float
    actual_delivery_date: Optional[date] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Sales Order Schemas
# ============================================================================

class SalesOrderBase(BaseModel):
    """Base schema for Sales Order."""
    customer_id: int
    order_date: date
    required_date: Optional[date] = None
    shipping_address: Optional[str] = None
    currency: str = Field(default="USD", max_length=3)


class SalesOrderCreate(SalesOrderBase):
    """Schema for creating a Sales Order."""
    pass


class SalesOrderResponse(SalesOrderBase):
    """Schema for Sales Order response."""
    id: int
    order_number: str
    status: str
    total_amount: float
    shipped_date: Optional[date] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
