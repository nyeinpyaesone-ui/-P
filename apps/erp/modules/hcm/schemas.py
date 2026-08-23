"""HCM Schemas - Pydantic Models for Human Capital Management API"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import date, datetime


# ============================================================================
# Employee Schemas
# ============================================================================

class EmployeeBase(BaseModel):
    """Base schema for Employee."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    hire_date: date
    job_title: Optional[str] = Field(None, max_length=100)
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    salary: Optional[float] = Field(None, ge=0)
    currency: str = Field(default="USD", max_length=3)


class EmployeeCreate(EmployeeBase):
    """Schema for creating an Employee."""
    pass


class EmployeeResponse(EmployeeBase):
    """Schema for Employee response."""
    id: int
    employee_code: str
    status: str
    termination_date: Optional[date] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Department Schemas
# ============================================================================

class DepartmentBase(BaseModel):
    """Base schema for Department."""
    department_name: str = Field(..., min_length=1, max_length=255)
    parent_department_id: Optional[int] = None
    cost_center: Optional[str] = Field(None, max_length=50)
    is_active: bool = True


class DepartmentCreate(DepartmentBase):
    """Schema for creating a Department."""
    pass


class DepartmentResponse(DepartmentBase):
    """Schema for Department response."""
    id: int
    department_code: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Payroll Schemas
# ============================================================================

class PayrollBase(BaseModel):
    """Base schema for Payroll."""
    employee_id: int
    pay_period_start: date
    pay_period_end: date
    pay_date: date
    gross_salary: float = Field(..., ge=0)
    net_salary: float = Field(..., ge=0)
    tax_deduction: float = Field(default=0.0, ge=0)
    other_deductions: float = Field(default=0.0, ge=0)
    bonuses: float = Field(default=0.0, ge=0)
    currency: str = Field(default="USD", max_length=3)


class PayrollCreate(PayrollBase):
    """Schema for creating a Payroll record."""
    pass


class PayrollResponse(PayrollBase):
    """Schema for Payroll response."""
    id: int
    payroll_id: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
