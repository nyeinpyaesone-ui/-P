"""Finance Router - API Endpoints for GL, AP/AR"""
from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()

@router.get("/", summary="List Accounts")
async def list_accounts():
    return {"accounts": [], "total": 0}

@router.get("/summary", summary="Financial Summary")
async def financial_summary():
    return {
        "total_assets": 0,
        "total_liabilities": 0,
        "equity": 0,
        "revenue": 0,
        "expenses": 0
    }

@router.post("/journal", summary="Create Journal Entry")
async def create_journal_entry(entry: dict):
    return {"status": "created", "id": 1}