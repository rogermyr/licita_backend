"""
Módulo de modelos SQLAlchemy.
Centraliza todas as definições de modelos do projeto.
"""
from .base import Base

# Importa todos os modelos para que sejam registrados no ORM
from .user import Usuario, ClienteConfig
from .licitacao import LicitacaoRaw, LicitacaoItem
from .tracking import Acompanhamento, OportunidadeMatch

# Exporta todas as classes para facilitar imports
__all__ = [
    'Base',
    'Usuario',
    'ClienteConfig',
    'LicitacaoRaw',
    'LicitacaoItem',
    'Acompanhamento',
    'OportunidadeMatch',
]