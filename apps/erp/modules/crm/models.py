"""CRM Models - Customer Relationship Management"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, date
from typing import Optional, List
from apps.erp.framework.database.models import Base, BaseAuditModel


class LeadStatus:
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    CONVERTED = "converted"


class Lead(BaseAuditModel):
    """Sales Leads - Potential customers."""
    
    __tablename__ = "crm_leads"
    
    lead_number = Column(String(50), unique=True, nullable=False)
    lead_source = Column(String(100), nullable=True)
    company_name = Column(String(255), nullable=True)
    contact_name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    estimated_value = Column(Numeric(19, 2), nullable=True)
    probability = Column(Integer, default=0)
    status = Column(String(20), default=LeadStatus.NEW)
    assigned_to_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    notes = Column(Text, nullable=True)


class OpportunityStage:
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class Opportunity(BaseAuditModel):
    """Sales Opportunities - Active deals."""
    
    __tablename__ = "crm_opportunities"
    
    opportunity_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    opportunity_name = Column(String(255), nullable=False)
    stage = Column(String(50), default=OpportunityStage.PROSPECTING)
    estimated_value = Column(Numeric(19, 2), nullable=False)
    probability = Column(Integer, default=0)
    expected_close_date = Column(Date, nullable=True)
    actual_close_date = Column(Date, nullable=True)
    assigned_to_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    description = Column(Text, nullable=True)


class SupportTicketPriority:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SupportTicketStatus:
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING_CUSTOMER = "pending_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"


class SupportTicket(BaseAuditModel):
    """Customer Support Tickets."""
    
    __tablename__ = "crm_support_tickets"
    
    ticket_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default=SupportTicketPriority.MEDIUM)
    status = Column(String(20), default=SupportTicketStatus.OPEN)
    category = Column(String(100), nullable=True)
    assigned_to_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    opened_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)


class InteractionType:
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    NOTE = "note"
    OTHER = "other"


class Interaction(BaseAuditModel):
    """Customer Interactions - Communication history."""
    
    __tablename__ = "crm_interactions"
    
    interaction_type = Column(String(50), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    lead_id = Column(Integer, ForeignKey("crm_leads.id"), nullable=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    interaction_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    subject = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    follow_up_date = Column(Date, nullable=True)
