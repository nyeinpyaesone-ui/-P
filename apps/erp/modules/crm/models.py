"""CRM Models"""
from sqlalchemy import Column, Integer, String
from apps.erp.framework.database.models import Base
class Item(Base):
    __tablename__ = "crm_items"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
