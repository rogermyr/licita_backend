# app/models/__init__.py

from .base import Base # Exporta a Base

# Importa TODOS os modelos para que sejam registrados no ORM
from .user import *
from .licitacao import *
from .tracking import *