# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base # Importa a base do nosso novo módulo

# --- TABELA: USUÁRIOS ---
class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    senha_hash = Column(String, nullable=False) 
    nome_completo = Column(String, nullable=False)
    telefone = Column(String, nullable=False) 
    cpf = Column(String, unique=True, nullable=False) 
    cargo = Column(String, nullable=True)
    data_cadastro = Column(DateTime, default=datetime.now)

# --- CONFIGURAÇÕES (VINCULADAS AO USUÁRIO) ---
class ClienteConfig(Base):
    __tablename__ = 'cliente_configs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('usuarios.id'))
    nome_perfil = Column(String)
    palavras_chave = Column(Text)
    palavras_negativas = Column(Text)
    
    usuario = relationship("Usuario")