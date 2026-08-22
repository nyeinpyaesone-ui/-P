"""
ERP03 Engine Commands Package
Provides CLI commands and database operations for the ERP system.
"""
from apps.erp.engine.commands.seed import seed_database

__all__ = ["seed_database"]
