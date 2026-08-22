"""Finance Schemas - Pydantic Models for API"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AccountBase(BaseModel):
    code: str
    name: str
    type: str

class AccountCreate(AccountBase):
    pass

class AccountResponse(AccountBase):
    id: int
    balance: float
    created_at: datetime
    class Config:
        from_attributes = True

class JournalEntryBase(BaseModel):
    description: str

class JournalEntryCreate(JournalEntryBase):
    pass

class TransactionBase(BaseModel):
    account_id: int
    debit: float = 0
    credit: float = 0