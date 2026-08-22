"""SCM Router"""
from fastapi import APIRouter
router = APIRouter()
@router.get("/", summary="List Items")
async def list_items():
    return {"items": [], "total": 0}
