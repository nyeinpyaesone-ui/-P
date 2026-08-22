"""HCM Models - Employees, Payroll, Departments"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from apps.erp.framework.database.models import Base

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    employee_number = Column(String(20), unique=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100))
    department_id = Column(Integer, ForeignKey("departments.id"))
    hire_date = Column(Date)
    salary = Column(Numeric(10, 2))
    status = Column(String(20))  # active, terminated, leave

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    code = Column(String(20))

class Payroll(Base):
    __tablename__ = "payroll"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    period_start = Column(Date)
    period_end = Column(Date)
    gross_pay = Column(Numeric(10, 2))
    net_pay = Column(Numeric(10, 2))
    paid_date = Column(DateTime(timezone=True))
