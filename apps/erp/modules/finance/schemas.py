"""Finance Schemas - Pydantic Models for API"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


# ============================================================================
# Account Schemas
# ============================================================================

class AccountBase(BaseModel):
    """Base schema for Account."""
    account_code: str = Field(..., min_length=1, max_length=50)
    account_name: str = Field(..., min_length=1, max_length=255)
    account_type: str = Field(..., description="asset, liability, equity, revenue, expense")
    currency: str = Field(default="USD", max_length=3)
    is_active: bool = True


class AccountCreate(AccountBase):
    """Schema for creating an Account."""
    pass


class AccountResponse(AccountBase):
    """Schema for Account response."""
    id: int
    balance: float = 0.0
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Journal Entry Schemas
# ============================================================================

class JournalEntryLineBase(BaseModel):
    """Base schema for Journal Entry Line."""
    account_id: int
    line_description: Optional[str] = Field(None, max_length=255)
    debit_amount: float = Field(default=0.0, ge=0)
    credit_amount: float = Field(default=0.0, ge=0)


class JournalEntryLineCreate(JournalEntryLineBase):
    """Schema for creating a Journal Entry Line."""
    pass


class JournalEntryBase(BaseModel):
    """Base schema for Journal Entry."""
    entry_date: date
    description: Optional[str] = None
    reference: Optional[str] = Field(None, max_length=100)


class JournalEntryCreate(JournalEntryBase):
    """Schema for creating a Journal Entry."""
    lines: list[JournalEntryLineCreate] = []


class JournalEntryResponse(JournalEntryBase):
    """Schema for Journal Entry response."""
    id: int
    entry_number: str
    status: str = "draft"
    total_debit: float = 0.0
    total_credit: float = 0.0
    is_balanced: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Transaction Schemas
# ============================================================================

class TransactionBase(BaseModel):
    """Base schema for Transaction."""
    account_id: int
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    transaction_type: str = Field(..., max_length=50)
    reference: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None