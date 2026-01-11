# api/index.py
import sys
import os

# Adiciona a raiz do projeto ao path para encontrar a pasta 'app'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Importa o app FastAPI
from app.main import app

# APAGUE A LINHA: handler = app
# Deixe apenas o import acima. A Vercel encontrará a variável 'app' sozinha.