from typing import Generator
# NOVO: Importe Depends do FastAPI
from fastapi import Depends 
# Supondo que você use SQLAlchemy, ajuste conforme seu ORM real
from sqlalchemy.orm import Session 

# 1. Importar as Classes das Camadas Core e Infraestrutura
from app.core.use_cases.adicionar_acompanhamento import CasoDeUsoAdicionarAcompanhamento
from app.db.repositories.licitacao_repo import LicitacaoRepositorioSQLAlchemy 
# Assumindo que você tem uma função para obter a sessão do DB
# VERIFIQUE O CAMINHO CORRETO: pode ser app.db.session.get_db
from app.db.session import get_db 

# Função que será usada no Depends() do FastAPI
def get_acompanhamento_use_case(db: Session = Depends(get_db)) -> CasoDeUsoAdicionarAcompanhamento:
    """
    Dependency Injector que constrói o Caso de Uso de Acompanhamento.
    """
    # 2. Instancia o Repositório Concreto (Adapter)
    repositorio = LicitacaoRepositorioSQLAlchemy(db_session=db)
    
    # 3. Instancia o Caso de Uso (Core), injetando o Repositório
    use_case = CasoDeUsoAdicionarAcompanhamento(repositorio=repositorio)
    
    return use_case