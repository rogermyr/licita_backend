"""
Módulo de schemas Pydantic.
Define os modelos de validação e serialização da API.
"""
# Exporta schemas principais de schemas.py
from .schemas import (
    UserCreate,
    PerfilSchema,
    PerfilResponse,
    VarreduraRequest,
    MatchResponse,
    VarreduraPaginadaResponse,
    CursorInfo,
    ItemAcompanhadoResponse,
    AcompanhamentoAction,
    SistemaResponse,
)

# Exporta schemas de user.py (UserResponse de user.py tem prioridade)
from .user import UserResponse, UserUpdate

__all__ = [
    'UserCreate',
    'UserResponse',
    'UserUpdate',
    'PerfilSchema',
    'PerfilResponse',
    'VarreduraRequest',
    'MatchResponse',
    'VarreduraPaginadaResponse',
    'CursorInfo',
    'ItemAcompanhadoResponse',
    'AcompanhamentoAction',
    'SistemaResponse',
]

# NOTA: LicitacaoCreate e LicitacaoResponse parecem estar faltando em schemas.py
# Eles precisam ser adicionados ou importados de outro lugar se necessário
