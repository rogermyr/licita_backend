"""
Módulo de banco de dados.
Centraliza funcionalidades relacionadas ao banco de dados.
"""
from .base import Base
from .session import SessionLocal, engine, get_db

__all__ = ['Base', 'SessionLocal', 'engine', 'get_db']
