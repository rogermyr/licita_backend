"""
Handler serverless para o Vercel.
Este arquivo funciona como ponto de entrada para todas as requisições.
"""
import sys
import os

# Adiciona a raiz do projeto e o diretório app ao path do Python
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
app_dir = os.path.join(project_root, 'app')

# Adiciona ambos ao sys.path para garantir imports corretos
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Importa o app FastAPI
from app.main import app

# O Vercel Python runtime detecta automaticamente o app FastAPI
# Exporta explicitamente para compatibilidade
__all__ = ['app']
