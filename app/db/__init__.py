"""
Módulo de banco de dados.
Centraliza funcionalidades relacionadas ao banco de dados.
"""
from app.db.base import Base
from app.db.session import SessionLocal, engine, get_db

__all__ = ['Base', 'SessionLocal', 'engine', 'get_db']
