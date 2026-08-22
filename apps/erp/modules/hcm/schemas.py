"""HCM Schemas - Pydantic Models"""
from pydantic import BaseModel
from datetime import date, datetime

class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    email: str

class EmployeeCreate(EmployeeBase):
    department_id: int
    hire_date: date
    salary: float

class EmployeeResponse(EmployeeBase):
    id: int
    employee_number: str
    status: str

class PayrollBase(BaseModel):
    employee_id: int
    period_start: date
    period_end: date
    gross_pay: float
