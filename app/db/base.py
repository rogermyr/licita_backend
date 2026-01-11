"""
Base declarativa centralizada para modelos SQLAlchemy.
Esta Base é exportada de models.base para manter compatibilidade.
"""
from app.models.base import Base

__all__ = ['Base']
