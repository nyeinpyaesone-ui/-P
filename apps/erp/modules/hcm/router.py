"""HCM Router - Employee and Payroll Endpoints"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/employees", summary="List Employees")
async def list_employees():
    return {"employees": [], "total": 0}

@router.get("/payroll", summary="List Payroll Records")
async def list_payroll():
    return {"records": []}

@router.post("/employees", summary="Create Employee")
async def create_employee(employee: dict):
    return {"status": "created", "id": 1}
