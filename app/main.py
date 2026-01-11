# app/main.py
from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text 
import logging
from app.db.session import get_db, engine # Adicione 'engine' aqui
from app.db.base import Base              # Importe a Base
# Importe explicitamente os modelos para garantir o registro no Metadata
from app import models

# Tente criar as tabelas com um log para depuração
try:
    print("Iniciando verificação de tabelas...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas verificadas/criadas com sucesso.")
except Exception as e:
    print(f"ERRO AO CRIAR TABELAS: {e}")



# Importa as configurações
from core.config import CORS_SETTINGS

# Importa os roteadores (endpoints)
from api.endpoints import auth, profiles, search, ia, acompanhamento
from api.endpoints import user as user_router # NOVO: Importa o novo roteador de usuário

# 1. Configuração Básica do Logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

API_PREFIX = "/api" 

app = FastAPI(
    title="Licitou API",
    description="API para monitoramento de licitações públicas.",
    version="1.0.0",
    docs_url=f"{API_PREFIX}/docs",
    redoc_url=f"{API_PREFIX}/redoc"
)

# Adiciona o middleware CORS
app.add_middleware(CORSMiddleware, **CORS_SETTINGS)


# Inclui as rotas, aplicando o prefixo /api
app.include_router(auth.router, prefix=API_PREFIX) 
app.include_router(profiles.router, prefix=f"{API_PREFIX}/perfis", tags=["perfis"]) 
app.include_router(search.router, prefix=API_PREFIX, tags=["search"]) 
app.include_router(ia.router, prefix=f"{API_PREFIX}/ia", tags=["IA Analysis"]) 
app.include_router(acompanhamento.router, prefix=API_PREFIX) 

# CRÍTICO: INCLUI A ROTA DE USUÁRIO
# Rota /api/users/me (Conforme definido no prefixo do user.py)
app.include_router(user_router.router, prefix=API_PREFIX) # MODIFICADO

@app.get(f"{API_PREFIX}/")
def read_root():
    return {"message": "API Licitou rodando!"}

@app.get(f"{API_PREFIX}/db-status", tags=["Debug"], status_code=status.HTTP_200_OK)
async def check_db_connection(db: Session = Depends(get_db)):
    """Verifica o status da conexão com o PostgreSQL e as credenciais."""
    
    try:
        db.execute(text("SELECT 1;")) 
        
        return {
            "status": "UP",
            "db_engine": "PostgreSQL",
            "message": "Conexão com o banco de dados e credenciais verificadas com sucesso."
        }
        
    except Exception as e:
        print(f"ERRO FATAL DE CONEXÃO AO DB: {e}") 
        
        return {
            "status": "DOWN",
            "error": "Falha ao autenticar ou conectar ao RDS",
            "details": f"Detalhe: {str(e)}",
            "guia": "Verifique o SG do RDS e a DATABASE_URL no Elastic Beanstalk."
        }, status.HTTP_500_INTERNAL_SERVER_ERROR