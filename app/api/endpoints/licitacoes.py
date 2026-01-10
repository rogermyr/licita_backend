from fastapi import APIRouter, Depends, HTTPException, status
# Importações necessárias para Tipagem e Configuração
from typing import Annotated 

# 1. Definição do Router
# Este passo define a variável 'router' que será usada nos decoradores.
router = APIRouter(prefix="/licitacoes", tags=["Acompanhamento de Licitações"])

# 2. Importações de Camadas Inferiores (Core e DB)
# Ajuste o caminho 'app.schemas.schemas' se o seu arquivo Pydantic estiver em outro local.
from schemas.schemas import LicitacaoCreate, LicitacaoResponse 
from core.use_cases.adicionar_acompanhamento import (
    CasoDeUsoAdicionarAcompanhamento, 
    LicitacaoJaAcompanhadaError
)
# Assumindo que você tem uma função de dependência para injetar o Caso de Uso
from db.dependencies import get_acompanhamento_use_case 

# 1. Obter o Usuário/ID a partir do token (Definido em app/api/dependencies.py ou app/core/security.py)
from core.security import get_current_user
from models import Usuario

# 3. Definição do Endpoint POST

@router.post(
    "/acompanhar", 
    response_model=LicitacaoResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Adiciona um Match de Licitação para acompanhamento interno."
)
def adicionar_licitacao_acompanhamento(
    licitacao_in: LicitacaoCreate,
    current_user: Usuario = Depends(get_current_user), 
    use_case: CasoDeUsoAdicionarAcompanhamento = Depends(get_acompanhamento_use_case)
):
    try:
        # 1. Chamada ao Caso de Uso (Execução da lógica de negócio)
        licitacao_salva = use_case.executar(
            id_match_externo=licitacao_in.id_match_externo,
            fonte=licitacao_in.fonte_dados,
            objeto=licitacao_in.objeto_licitacao,
            data_encerramento=licitacao_in.data_encerramento,
            valor_estimado=licitacao_in.valor_estimado,
            link_pncp=licitacao_in.link_pncp,
            user_id=current_user.id # NOVO: Passando o ID do usuário para o Caso de Uso
        )
        
        return licitacao_salva
        
    except LicitacaoJaAcompanhadaError as e:
        # Tratamento do erro de negócio específico (409 Conflict)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        # LOG TEMPORÁRIO PARA DEBUG
        import logging
        logging.error(f"Erro CRÍTICO no POST /licitacoes/acompanhar: {e}", exc_info=True)
        # FIM LOG TEMPORÁRIO
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro interno. Tente novamente mais tarde."
        )