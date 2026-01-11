# app/api/endpoints/search.py

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from sqlalchemy import text 

from typing import List, Any, Optional
import logging

# Importa as dependências e módulos
from app.db.session import get_db
from app.core.security import get_current_user

# Schemas
from app.schemas.schemas import (
    VarreduraRequest, 
    MatchResponse, 
    VarreduraPaginadaResponse,
    CursorInfo 
)

# Importa a lógica de busca
from app.crud.search_logic import build_and_execute_search_query 
from app.models.user import Usuario, ClienteConfig 

# Importa a função de processamento da camada de serviço
from app.services.search_processor import process_search_results 

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Busca e Filtros"]
)

# 1. Rota de Varredura Principal (OTIMIZADA PARA SILVER)
@router.post("/executar-varredura", response_model=VarreduraPaginadaResponse)
def rodar_varredura(
    dados: VarreduraRequest, 
    user: Usuario = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Executa a busca otimizada na camada SILVER.
    Permite busca via perfil cadastrado ou termos personalizados (Ad-hoc).
    """
    logger.info(
        f"🔍 Varredura Silver | User: {user.id} | "
        f"Perfis: {dados.perfil_ids} | "
        f"Custom: {dados.custom_keywords} | "
        f"Valores: {dados.valor_min} - {dados.valor_max}"
    )
    
    # 1. SEGURANÇA E VALIDAÇÃO
    perfis = []
    if dados.perfil_ids:
        perfis = db.query(ClienteConfig).filter(
            ClienteConfig.id.in_(dados.perfil_ids), 
            ClienteConfig.user_id == user.id
        ).all()
        
        if not perfis and not dados.custom_keywords:
            raise HTTPException(
                status_code=400, 
                detail="Perfis inválidos ou não pertencem ao usuário."
            )

    if not perfis and not dados.custom_keywords:
        raise HTTPException(
            status_code=400, 
            detail="Selecione um perfil ou digite termos de busca personalizados para iniciar."
        )

    # ---------------------------------------------------------------------
    # LÓGICA DE BUSCA ITERATIVA
    # ---------------------------------------------------------------------
    LIMITE_PAGINA = dados.limit 
    MAX_DB_LIMIT = LIMITE_PAGINA + 20 
    MAX_SEARCH_ITERATIONS = 3 
    
    resultados_finais: List[MatchResponse] = []
    current_request_data = dados.model_copy(deep=True) 
    total_count = 0 
    ultimo_item_bruto = None

    for iteration in range(MAX_SEARCH_ITERATIONS):
        if len(resultados_finais) >= LIMITE_PAGINA:
            break
            
        current_request_data.limit = MAX_DB_LIMIT
        
        # 1. Busca um bloco da tabela SILVER (via crud/search_logic.py)
        resultados_brutos, current_total_count = build_and_execute_search_query(
            db, perfis, current_request_data
        )
        
        if iteration == 0:
            total_count = current_total_count
            
        if not resultados_brutos:
            break
            
        # 2. Processamento (MODIFICADO: Passando custom_keywords para o processador)
        # Isso garante que a validação de precisão pós-SQL use os termos que você digitou
        lista_processada = process_search_results(
            db, 
            perfis, 
            resultados_brutos,
            custom_keywords=dados.custom_keywords  # // NOVO: Campo adicionado aqui
        )
        resultados_finais.extend(lista_processada)
        
        # 3. Atualiza o Keyset para a próxima página
        ultimo_item_bruto = resultados_brutos[-1]
        
        try:
            current_request_data.last_valor_total = float(ultimo_item_bruto.valor_total_item or 0)
            current_request_data.last_item_id = ultimo_item_bruto.item_id
            current_request_data.offset = 0
        except AttributeError as e:
            logger.error(f"Erro no Keyset: {e}")
            break

    # ---------------------------------------------------------------------
    # PAGINAÇÃO E RESPOSTA
    # ---------------------------------------------------------------------
    lista_final_paginada = resultados_finais[:LIMITE_PAGINA]
    cursor_info = None
    
    if len(lista_final_paginada) == LIMITE_PAGINA and ultimo_item_bruto:
        cursor_info = CursorInfo(
            next_last_valor_total=float(current_request_data.last_valor_total), 
            next_last_item_id=current_request_data.last_item_id
        )

    return VarreduraPaginadaResponse(
        total_items=total_count, 
        limit=dados.limit,
        offset=dados.offset + dados.limit, 
        resultados=lista_final_paginada,
        cursor=cursor_info 
    )


# 2. Rota para Listar UFs Disponíveis
@router.get("/ufs-disponiveis", response_model=List[str])
def listar_ufs(db: Session = Depends(get_db)):
    """
    Retorna a lista de UFs extraída diretamente da coluna indexada na Silver.
    """
    sql = text("""
        SELECT DISTINCT uf_sigla 
        FROM silver_licitacoes 
        WHERE uf_sigla IS NOT NULL 
        ORDER BY uf_sigla
    """)
    
    try: 
        resultados = db.execute(sql).fetchall()
        ufs = [row.uf_sigla for row in resultados if row.uf_sigla and row.uf_sigla != 'BR']
        return ufs
    except Exception as e:
        logger.error(f"Falha ao consultar UFs na Silver: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar localidades.")