"""
Módulo de modelos SQLAlchemy.
Centraliza todas as definições de modelos do projeto.
"""
from app.models.base import Base

# Importa todos os modelos para que sejam registrados no ORM
from app.models.user import Usuario, ClienteConfig
from app.models.licitacao import LicitacaoRaw, LicitacaoItem
from app.models.tracking import Acompanhamento, OportunidadeMatch

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