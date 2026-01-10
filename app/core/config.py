# app/core/config.py
from datetime import timedelta
from decouple import config # Recomendado para variáveis de ambiente

SECRET_KEY = config("SECRET_KEY", default="segredo_super_secreto_troque_isso")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

# Configurações do CORS
CORS_SETTINGS = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}