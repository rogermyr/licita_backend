# app/core/security.py

import bcrypt
from datetime import datetime, timedelta
import logging
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

# Importações internas
from core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from db.session import get_db
from models import Usuario 

logger = logging.getLogger(__name__)

# Configuração do esquema OAuth2 para injeção de dependência
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

# DEFINIÇÃO DA TOLERÂNCIA (LEEWAY)
# Permite que o token seja aceito mesmo se o relógio estiver alguns segundos defasado.
CLOCK_DRIFT_TOLERANCE_SECONDS = 60 # NOVO

# =======================================================
# FUNÇÕES DE HASHING DE SENHA (BCRYPT)
# =======================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto puro corresponde ao hash armazenado."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Gera o hash seguro de uma senha."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


# =======================================================
# FUNÇÕES DE AUTENTICAÇÃO (JWT)
# =======================================================

def criar_token(data: dict) -> str:
    # DEBUG: Chave de criação
    logger.info(f"🔑 CRIAÇÃO (Chave): {SECRET_KEY[:10]}...") 
    """Cria um token JWT com tempo de expiração."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # IMPORTANTE: A criação NÃO usa o leeway, apenas a decodificação.
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    # DEBUG: Chave de verificação
    logger.info(f"🔑 VERIFICAÇÃO (Chave): {SECRET_KEY[:10]}...")
    """Decodifica o token e retorna o usuário do DB."""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # ----------------------------------------------------
    # FIX: Check defensivo contra tokens malformados/vazios
    if not token or token.count('.') < 2: 
        logger.error(f"❌ Token extraído está vazio ou malformado (segments < 2). Token recebido: {token}")
        raise credentials_exception
    # ----------------------------------------------------
    
    try:
        # Tenta decodificar o token
        # NOVO: Injetando tolerância (leeway) para evitar clock drift
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM],
            options={"leeway": CLOCK_DRIFT_TOLERANCE_SECONDS} # NOVO
        )
        
        username: str = payload.get("sub")
        
        if username is None: 
            logger.warning(f"Token decodificado, mas sem 'sub'. Payload: {payload}")
            raise credentials_exception
            
        logger.info(f"✅ Token decodificado com sucesso. Tentando buscar usuário: {username}")

    except JWTError as e:
        # CAPTURA O ERRO DE SEGURANÇA (EX: EXPIRADO, ASSINATURA INVÁLIDA)
        logger.error(f"❌ Falha crítica na decodificação JWT: {e}") 
        raise credentials_exception
        
    # Busca o usuário no DB
    user = db.query(Usuario).filter(Usuario.username == username).first()
    
    if user is None: 
        logger.warning(f"❌ Usuário {username} encontrado no token, mas não no banco de dados.")
        raise credentials_exception
    return user