"""Compatibility import used by AB's authentication modules and tests.

The actual implementation lives in app.db.session so there is only one
dependency object for FastAPI overrides and production routes.
"""
from app.db.session import get_db

__all__ = ["get_db"]
