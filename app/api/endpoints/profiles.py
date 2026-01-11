# app/api/endpoints/profiles.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Importa as dependências e módulos
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.schemas import PerfilSchema, PerfilResponse
from app.models.user import Usuario, ClienteConfig

# Cria o roteador do FastAPI
# Nota: O prefixo "/perfis" já será aplicado em app/main.py,
# então aqui as rotas internas são definidas em relação ao prefixo.
router = APIRouter(
    tags=["Perfis de Cliente"]
)

# --- Rotas CRUD ---

@router.get("", response_model=List[PerfilResponse])
def listar_perfis(user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lista todos os perfis de busca associados ao usuário logado."""
    return db.query(ClienteConfig).filter(ClienteConfig.user_id == user.id).all()

@router.post("", response_model=PerfilResponse, status_code=status.HTTP_201_CREATED)
def criar_perfil(perfil: PerfilSchema, user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """Cria um novo perfil de busca para o usuário."""
    novo = ClienteConfig(
        user_id=user.id, 
        nome_perfil=perfil.nome_perfil, 
        palavras_chave=perfil.palavras_chave, 
        palavras_negativas=perfil.palavras_negativas
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

@router.put("/{perfil_id}", response_model=PerfilResponse)
def atualizar_perfil(perfil_id: int, perfil_atualizado: PerfilSchema, user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """Atualiza um perfil existente pertencente ao usuário."""
    perfil_db = db.query(ClienteConfig).filter(ClienteConfig.id == perfil_id, ClienteConfig.user_id == user.id).first()
    
    if not perfil_db: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil não encontrado ou acesso negado.")
    
    perfil_db.nome_perfil = perfil_atualizado.nome_perfil
    perfil_db.palavras_chave = perfil_atualizado.palavras_chave
    perfil_db.palavras_negativas = perfil_atualizado.palavras_negativas
    
    db.commit()
    db.refresh(perfil_db)
    return perfil_db

@router.delete("/{perfil_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_perfil(perfil_id: int, user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """Deleta um perfil existente pertencente ao usuário."""
    perfil = db.query(ClienteConfig).filter(ClienteConfig.id == perfil_id, ClienteConfig.user_id == user.id).first()
    
    if not perfil: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil não encontrado ou acesso negado.")
        
    db.delete(perfil)
    db.commit()
    return {"msg": "Deletado"}