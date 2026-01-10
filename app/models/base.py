"""
Base declarativa para modelos SQLAlchemy.
Centralizada aqui e re-exportada em db.base para compatibilidade.
"""
from sqlalchemy.ext.declarative import declarative_base
from typing import Any

# Tipagem para a classe Base
class CustomBase:
    __name__: str
    id: Any
    
# Cria o objeto Base que todos os modelos ORM devem herdar
Base = declarative_base(cls=CustomBase)

__all__ = ['Base']