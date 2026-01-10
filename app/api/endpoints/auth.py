# app/api/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging # NOVO: Adicionado logging para debug

# Importa as funções de segurança
from bcrypt import gensalt, hashpw, checkpw 

# Importa as dependências e módulos do CORE/DB
from db.session import get_db
from core.security import criar_token, get_current_user
from schemas.schemas import UserCreate # Schema ATUALIZADO
from models.user import Usuario # IMPORTAÇÃO CORRIGIDA


logger = logging.getLogger(__name__)

# Cria o roteador do FastAPI para agrupar as rotas de autenticação
router = APIRouter(
    tags=["Autenticação"],
    prefix="" 
)

@router.post("/registrar", status_code=status.HTTP_201_CREATED)
def registrar(user: UserCreate, db: Session = Depends(get_db)):
    """
    Cria um novo usuário com senha hasheada e dados completos de perfil.
    """
    # 1. Verifica se o usuário (email) já existe
    if db.query(Usuario).filter(Usuario.username == user.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já registrado.")
    
    # 2. Gera o hash da senha
    salt = gensalt()
    hash_senha = hashpw(user.password.encode('utf-8'), salt)
    
    try:
        # 3. Cria e salva o novo usuário, populando todos os campos // MODIFICADO CRÍTICO
        novo = Usuario(
            username=user.email,  # Usamos o email como identificador (username)
            senha_hash=hash_senha,
            nome_completo=user.nome_completo,  # NOVO
            telefone=user.telefone,            # NOVO
            cpf=user.cpf,                      # NOVO
            cargo=user.cargo                   # NOVO
        )
        db.add(novo)
        db.commit()
        db.refresh(novo)
        
        logger.info(f"Novo usuário registrado: {novo.username}")
        
        return {"msg": "Usuário registrado com sucesso"}
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao salvar novo usuário no DB: {e}")
        # Se ocorrer um IntegrityError (por exemplo, CPF duplicado, se a coluna for unique)
        if "IntegrityError" in str(e):
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CPF ou Email já cadastrado.")
        
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao registrar usuário.")


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Gera e retorna um token JWT após validação das credenciais.
    """
    # 1. Busca o usuário pelo username (agora o email)
    user = db.query(Usuario).filter(Usuario.username == form_data.username).first()
    
    # 2. Valida o usuário e a senha
    if not user or not checkpw(form_data.password.encode('utf-8'), user.senha_hash.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Credenciais inválidas"
        )
    
    # 3. Cria o token JWT
    token = criar_token(data={"sub": user.username})
    
    # 4. Retorna o token de acesso
    return {"access_token": token, "token_type": "bearer"}

# --- Exemplo de Rota Protegida ---
@router.get("/users/me")
def read_users_me(current_user: Usuario = Depends(get_current_user)):
    """
    Rota de exemplo que usa a dependência get_current_user para verificar o token.
    """
    return {"username": current_user.username, "id": current_user.id}