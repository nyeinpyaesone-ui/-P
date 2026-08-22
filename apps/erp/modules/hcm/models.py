"""HCM Models - Human Capital Management: Employees, Departments, Payroll"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text, Date, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, date
from typing import Optional, List
from apps.erp.framework.database.models import Base, BaseAuditModel


class EmployeeStatus:
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"
    RETIRED = "retired"


class Employee(BaseAuditModel):
    """Employee Records - Core HCM structure."""
    
    __tablename__ = "hcm_employees"
    
    employee_code = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(50), nullable=True)
    hire_date = Column(Date, nullable=False)
    termination_date = Column(Date, nullable=True)
    job_title = Column(String(100), nullable=True)
    department_id = Column(Integer, ForeignKey("hcm_departments.id"), nullable=True)
    manager_id = Column(Integer, ForeignKey("hcm_employees.id"), nullable=True)
    status = Column(String(20), default=EmployeeStatus.ACTIVE)
    salary = Column(Numeric(19, 2), nullable=True)
    currency = Column(String(3), default="USD")


class Department(BaseAuditModel):
    """Organizational Departments."""
    
    __tablename__ = "hcm_departments"
    
    department_code = Column(String(50), unique=True, nullable=False)
    department_name = Column(String(255), nullable=False)
    parent_department_id = Column(Integer, ForeignKey("hcm_departments.id"), nullable=True)
    cost_center = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)


class Payroll(BaseAuditModel):
    """Payroll Processing - Salary payments and deductions."""
    
    __tablename__ = "hcm_payroll"
    
    payroll_id = Column(String(50), unique=True, nullable=False)
    employee_id = Column(Integer, ForeignKey("hcm_employees.id"), nullable=False)
    pay_period_start = Column(Date, nullable=False)
    pay_period_end = Column(Date, nullable=False)
    pay_date = Column(Date, nullable=False)
    gross_salary = Column(Numeric(19, 2), nullable=False)
    net_salary = Column(Numeric(19, 2), nullable=False)
    tax_deduction = Column(Numeric(19, 2), default=0.00)
    other_deductions = Column(Numeric(19, 2), default=0.00)
    bonuses = Column(Numeric(19, 2), default=0.00)
    status = Column(String(20), default="pending")
    currency = Column(String(3), default="USD")
