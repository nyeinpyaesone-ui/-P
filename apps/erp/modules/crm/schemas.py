"""CRM Schemas - Pydantic Models for Customer Relationship Management API"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import date, datetime


# ============================================================================
# Lead Schemas
# ============================================================================

class LeadBase(BaseModel):
    """Base schema for Lead."""
    contact_name: str = Field(..., min_length=1, max_length=255)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=50)
    company_name: Optional[str] = Field(None, max_length=255)
    lead_source: Optional[str] = Field(None, max_length=100)
    estimated_value: Optional[float] = Field(None, ge=0)
    probability: int = Field(default=0, ge=0, le=100)
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    """Schema for creating a Lead."""
    pass


class LeadResponse(LeadBase):
    """Schema for Lead response."""
    id: int
    lead_number: str
    status: str
    assigned_to_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Opportunity Schemas
# ============================================================================

class OpportunityBase(BaseModel):
    """Base schema for Opportunity."""
    opportunity_name: str = Field(..., min_length=1, max_length=255)
    customer_id: Optional[int] = None
    stage: str = Field(default="prospecting", max_length=50)
    estimated_value: float = Field(..., ge=0)
    probability: int = Field(default=0, ge=0, le=100)
    expected_close_date: Optional[date] = None
    description: Optional[str] = None


class OpportunityCreate(OpportunityBase):
    """Schema for creating an Opportunity."""
    pass


class OpportunityResponse(OpportunityBase):
    """Schema for Opportunity response."""
    id: int
    opportunity_number: str
    actual_close_date: Optional[date] = None
    assigned_to_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Support Ticket Schemas
# ============================================================================

class SupportTicketBase(BaseModel):
    """Base schema for Support Ticket."""
    subject: str = Field(..., min_length=1, max_length=255)
    description: str
    customer_id: int
    priority: str = Field(default="medium", max_length=20)
    category: Optional[str] = Field(None, max_length=100)


class SupportTicketCreate(SupportTicketBase):
    """Schema for creating a Support Ticket."""
    pass


class SupportTicketResponse(SupportTicketBase):
    """Schema for Support Ticket response."""
    id: int
    ticket_number: str
    status: str
    assigned_to_id: Optional[int] = None
    opened_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Interaction Schemas
# ============================================================================

class InteractionBase(BaseModel):
    """Base schema for Interaction."""
    interaction_type: str = Field(..., max_length=50)
    employee_id: int
    customer_id: Optional[int] = None
    lead_id: Optional[int] = None
    subject: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None
    follow_up_date: Optional[date] = None


class InteractionCreate(InteractionBase):
    """Schema for creating an Interaction."""
    pass


class InteractionResponse(InteractionBase):
    """Schema for Interaction response."""
    id: int
    interaction_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True
