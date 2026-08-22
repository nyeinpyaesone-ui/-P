"""Finance Router - API Endpoints for GL, AP/AR

Provides RESTful endpoints for financial operations including:
- Chart of Accounts management
- Journal Entry creation and retrieval
- Financial summaries
"""
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from apps.erp.main import AsyncSessionLocal

from .schemas import (
    AccountCreate, AccountResponse,
    JournalEntryCreate, JournalEntryResponse,
    TransactionBase,
)
from apps.erp.framework.database.models import Account, JournalEntry, JournalEntryLine, Transaction


def get_db_session_dependency():
    """Get database session dependency."""
    # This will be properly configured when the app starts
    from apps.erp.main import AsyncSessionLocal
    return AsyncSessionLocal()


router = APIRouter()


async def get_db():
    """Dependency for getting async database session."""
    from apps.erp.main import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@router.get("/accounts", response_model=List[AccountResponse], summary="List Accounts")
async def list_accounts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[dict]:
    """Retrieve all accounts in the chart of accounts.
    
    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        
    Returns:
        List of account records
    """
    result = await db.execute(select(Account).offset(skip).limit(limit))
    accounts = result.scalars().all()
    return accounts


@router.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED, summary="Create Account")
async def create_account(
    account: AccountCreate,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Create a new account in the chart of accounts.
    
    Args:
        account: Account data including code, name, type, and currency
        
    Returns:
        Created account with generated ID and timestamp
        
    Raises:
        HTTPException: If account code already exists
    """
    # Check for duplicate account code
    result = await db.execute(
        select(Account).where(Account.account_code == account.account_code)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Account code {account.account_code} already exists"
        )
    
    db_account = Account(**account.model_dump())
    db.add(db_account)
    await db.flush()
    await db.refresh(db_account)
    return db_account


@router.get("/summary", response_model=dict, summary="Financial Summary")
async def financial_summary(db: AsyncSession = Depends(get_db)) -> dict:
    """Get financial summary across all account types.
    
    Returns:
        Aggregated financial metrics including assets, liabilities, equity, revenue, and expenses
    """
    result = await db.execute(select(Account))
    accounts = result.scalars().all()
    
    summary = {
        "total_assets": 0.0,
        "total_liabilities": 0.0,
        "equity": 0.0,
        "revenue": 0.0,
        "expenses": 0.0
    }
    
    for account in accounts:
        if not account.is_deleted:
            account_type = account.account_type.value if hasattr(account.account_type, 'value') else str(account.account_type)
            if account_type == "asset":
                summary["total_assets"] += float(account.balance or 0)
            elif account_type == "liability":
                summary["total_liabilities"] += float(account.balance or 0)
            elif account_type == "equity":
                summary["equity"] += float(account.balance or 0)
            elif account_type == "revenue":
                summary["revenue"] += float(account.balance or 0)
            elif account_type == "expense":
                summary["expenses"] += float(account.balance or 0)
    
    return summary


@router.get("/journal-entries", response_model=List[JournalEntryResponse], summary="List Journal Entries")
async def list_journal_entries(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[dict]:
    """Retrieve all journal entries.
    
    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        
    Returns:
        List of journal entry records
    """
    result = await db.execute(select(JournalEntry).offset(skip).limit(limit))
    entries = result.scalars().all()
    return entries


@router.post("/journal-entries", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED, summary="Create Journal Entry")
async def create_journal_entry(
    entry: JournalEntryCreate,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Create a new journal entry with double-entry bookkeeping validation.
    
    Args:
        entry: Journal entry data including date, description, and line items
        
    Returns:
        Created journal entry with generated entry number
        
    Raises:
        HTTPException: If journal entry is not balanced (debits != credits)
    """
    from decimal import Decimal
    
    # Validate that debits equal credits
    total_debit = sum(line.debit_amount for line in entry.lines)
    total_credit = sum(line.credit_amount for line in entry.lines)
    
    if abs(total_debit - total_credit) > Decimal('0.01'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Journal entry not balanced. Debit: {total_debit}, Credit: {total_credit}"
        )
    
    # Generate entry number
    result = await db.execute(select(JournalEntry).order_by(JournalEntry.id.desc()).limit(1))
    last_entry = result.scalar_one_or_none()
    next_id = (last_entry.id if last_entry else 0) + 1
    entry_number = f"JE-{next_id:06d}"
    
    db_entry = JournalEntry(
        entry_number=entry_number,
        entry_date=entry.entry_date,
        description=entry.description,
        reference=entry.reference,
        status="draft"
    )
    
    db.add(db_entry)
    await db.flush()
    
    # Add journal entry lines
    for line in entry.lines:
        db_line = JournalEntryLine(
            journal_entry_id=db_entry.id,
            account_id=line.account_id,
            line_description=line.line_description,
            debit_amount=line.debit_amount,
            credit_amount=line.credit_amount
        )
        db.add(db_line)
    
    await db.flush()
    await db.refresh(db_entry)
    return db_entry