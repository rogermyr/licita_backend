from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError # NOVO: Importar para capturar erros de DB
from db.session import get_db
from core.security import get_current_user
from models.user import Usuario # Assumindo que Usuario está definido aqui
from schemas.user import UserResponse, UserUpdate
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Usuário"], prefix="/users")

# --- ROTA DE DIAGNÓSTICO (DEBUG) ---
@router.get("/db_health_check", response_model=UserResponse)
def check_db_connection(db: Session = Depends(get_db)):
    """
    [DIAGNÓSTICO] Tenta buscar um usuário conhecido no DB, ignorando a autenticação JWT.
    Objetivo: Isolar falhas de conexão ou query no RDS/PostgreSQL.
    """
    # Use o username que falhou na requisição JWT
    test_username = "rogerio.silva@gmail.com" 

    logger.info(f"Iniciando teste de saúde do DB para usuário: {test_username}")

    try:
        # 1. Teste de Busca (Query real)
        user = db.query(Usuario).filter(Usuario.username == test_username).first()
        
        if user is None:
            # Se a busca funcionou, mas não encontrou o usuário
            logger.error(f"❌ DB Teste Falhou: Usuário {test_username} não encontrado.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário de teste não encontrado no DB.")
        
        # 2. Teste de Conexão (Sucesso)
        logger.info(f"✅ DB Teste Sucesso! Usuário encontrado: {user.username}")
        return user
    
    except SQLAlchemyError as e:
        # Captura erros de rede, credenciais de DB, ou Pool Exausto
        logger.critical(f"❌ FALHA CRÍTICA NA CONEXÃO OU QUERY (SQLAlchemy): {e}", exc_info=True)
        # Retornamos um erro 503 (Serviço Indisponível) para indicar falha de infraestrutura
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail=f"Erro de Conexão com o Banco de Dados. Verifique logs para detalhes."
        )
    
    except Exception as e:
        logger.critical(f"❌ Erro Inesperado no Teste de DB: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno no servidor.")
# --- FIM ROTA DE DIAGNÓSTICO ---


# --- ROTAS DE PRODUÇÃO ---

@router.get("/eu", response_model=UserResponse)
def get_user_me(current_user: Usuario = Depends(get_current_user)):
    logger.info(f"Usuário: {current_user.nome_completo} | Cargo: {current_user.cargo}")
    return current_user

@router.put("/eu", response_model=UserResponse)
def update_user_me(
    user_data: UserUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza dados do perfil do usuário logado."""
    # Princípio SOLID (LSP) e Manutenibilidade: Usando setattr para atualização dinâmica
    for field, value in user_data.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user