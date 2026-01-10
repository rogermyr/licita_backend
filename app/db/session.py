from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import logging
# Obtém o logger para este módulo específico
logger = logging.getLogger(__name__)

# 1. Configuração da URL do Banco de Dados
# O ideal é puxar isso de variáveis de ambiente (app.core.config)
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:131194@localhost:5432/pncp_db"
)
# Oudbname" 
# Ou se for SQLite para desenvolvimento:
# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# Cria o Engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    # Para SQLite (necessário para threads): connect_args={"check_same_thread": False}
)

# Cria o SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Função geradora para obter a sessão (usada no FastAPI Depends)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()