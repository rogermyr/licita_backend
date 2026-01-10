# app/api/endpoints/acompanhamento.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

# Dependências
from db.session import get_db
from core.security import get_current_user 

# CRUD e Serviços
from crud.acompanhamento_logic import (
    get_acompanhamentos_by_user, 
    toggle_acompanhamento,
    check_item_is_acompanhado
)
from services.acompanhamento_processor import process_acompanhamento_list 

# Modelos e Schemas
from models.user import Usuario 
from schemas.schemas import (
    ItemAcompanhadoResponse, 
    AcompanhamentoAction,
    MatchResponse 
) 

router = APIRouter(
    prefix="/acompanhamento", 
    tags=["Acompanhamento de Licitações"]
)

# Rota 1: Listar Itens Acompanhados - COMPLETA COM ORDENAÇÃO
@router.get(
    "/", 
    response_model=List[ItemAcompanhadoResponse], 
    summary="Lista os itens de licitação em acompanhamento do usuário logado"
)
async def list_itens_acompanhados(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user), 
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100), 
    sort_by: Optional[str] = Query('data_encerramento', alias="sort_by"), 
    order: Optional[str] = Query('asc', alias="order")                     
):
    """
    Busca os registros de acompanhamento brutos, aplica ordenação e paginação, 
    e os processa para o formato MatchResponse.
    """
    
    # 1. Busca os registros de acompanhamento (Acompanhamento ORM)
    acompanhamentos_brutos = get_acompanhamentos_by_user(
        db=db,
        user_id=user.id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        order=order
    )
    
    if not acompanhamentos_brutos and skip > 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum item encontrado nesta página.")
        
    # 2. Processa os dados brutos (Item + Raw) para o formato de resposta MatchResponse
    itens_formatados = process_acompanhamento_list(acompanhamentos_brutos)
    
    return itens_formatados

# Rota 2: Marcar/Desmarcar um Item
@router.post("/toggle", status_code=status.HTTP_200_OK) 
def toggle_item_acompanhamento(
    data: AcompanhamentoAction,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marca ou desmarca um item de licitação para acompanhamento pelo usuário logado."""
    
    success = toggle_acompanhamento(db, user.id, data.item_id, data.acompanhar)
    
    if success:
        action = "marcado" if data.acompanhar else "desmarcado"
        return {"message": f"Item {data.item_id} {action} com sucesso."}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não foi possível realizar a ação para o item {data.item_id}. Item não encontrado ou erro de DB."
        )

# Rota 3: Checar Status 
@router.get("/acompanhamento/status/{item_id}", response_model=bool)
def get_acompanhamento_status(
    item_id: int,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verifica se um item específico está sendo acompanhado pelo usuário logado."""
    return check_item_is_acompanhado(db, user.id, item_id)