"""
ERP03 Configuration Settings

Centralized configuration management for all ERP modules.
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
APPS_DIR = BASE_DIR / "apps"

# Database configuration
DATABASE_CONFIG = {
    "user": os.getenv("POSTGRES_USER", "erp"),
    "password": os.getenv("POSTGRES_PASSWORD", "erp_secure_password_change_me"),
    "host": os.getenv("POSTGRES_HOST", "postgres"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "database": os.getenv("POSTGRES_DB", "erp_core"),
}

# Build database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@"
    f"{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
)

# Redis configuration
REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST", "redis"),
    "port": int(os.getenv("REDIS_PORT", "6379")),
    "password": os.getenv("REDIS_PASSWORD", None),
    "db": 0,
}

REDIS_URL = os.getenv("REDIS_URL", f"redis://{REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}/{REDIS_CONFIG['db']}")

# RabbitMQ configuration
RABBITMQ_CONFIG = {
    "user": os.getenv("RABBITMQ_DEFAULT_USER", "erp"),
    "password": os.getenv("RABBITMQ_DEFAULT_PASS", "erp_secure_password_change_me"),
    "host": os.getenv("RABBITMQ_HOST", "rabbitmq"),
    "port": int(os.getenv("RABBITMQ_PORT", "5672")),
}

RABBITMQ_URL = os.getenv(
    "RABBITMQ_URL",
    f"amqp://{RABBITMQ_CONFIG['user']}:{RABBITMQ_CONFIG['password']}@{RABBITMQ_CONFIG['host']}:{RABBITMQ_CONFIG['port']}//"
)

# Application settings
APP_ENV = os.getenv("APP_ENV", "production")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "change_this_to_a_secure_random_string")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")

# API configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Expected database schemas
EXPECTED_SCHEMAS = [
    "accounting",
    "sales",
    "inventory",
    "hr",
    "crm",
    "warehouse",
    "logistics",
    "reporting",
]

# Module configuration
MODULES = {
    "accounting": {"enabled": True, "schema": "accounting"},
    "sales": {"enabled": True, "schema": "sales"},
    "inventory": {"enabled": True, "schema": "inventory"},
    "hr": {"enabled": True, "schema": "hr"},
    "crm": {"enabled": True, "schema": "crm"},
    "warehouse": {"enabled": True, "schema": "warehouse"},
    "logistics": {"enabled": True, "schema": "logistics"},
    "reporting": {"enabled": True, "schema": "reporting"},
}


def get_database_url(schema: str | None = None) -> str:
    """Get database URL with optional schema."""
    if schema:
        return f"{DATABASE_URL}?options=-c%20search_path%3D{schema}"
    return DATABASE_URL


def is_production() -> bool:
    """Check if running in production environment."""
    return APP_ENV == "production"


def is_development() -> bool:
    """Check if running in development environment."""
    return APP_ENV == "development"
