# api/index.py
"""
Handler serverless para o Vercel.
Este arquivo funciona como ponto de entrada para todas as requisições.
"""
import sys
import os

# Adiciona APENAS a raiz do projeto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Importa o app FastAPI usando o caminho completo
from app.main import app

handler = app
