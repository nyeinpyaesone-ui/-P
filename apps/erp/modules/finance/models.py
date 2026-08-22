"""Finance Models - GL, AP/AR, Cash Management"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from apps.erp.framework.database.models import Base

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(20))  # asset, liability, equity, revenue, expense
    balance = Column(Numeric(15, 2), default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    description = Column(String(255))
    posted = Column(Boolean, default=False)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    entry_id = Column(Integer, ForeignKey("journal_entries.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"))
    debit = Column(Numeric(15, 2), default=0)
    credit = Column(Numeric(15, 2), default=0)