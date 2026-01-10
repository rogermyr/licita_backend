# models.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.schema import UniqueConstraint 
from datetime import datetime
from db.base import Base 

# --- NOVA TABELA: USUÁRIOS ---
class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False) # Armazena o E-MAIL
    senha_hash = Column(String, nullable=False) 
    
    # NOVAS COLUNAS DE REGISTRO // MODIFICADO
    nome_completo = Column(String, nullable=False)
    telefone = Column(String, nullable=False) 
    cpf = Column(String, unique=True, nullable=False) # Adicionado UniqueConstraint no ORM
    cargo = Column(String, nullable=True)
    
    data_cadastro = Column(DateTime, default=datetime.now)

# --- CONFIGURAÇÕES (VINCULADAS AO USUÁRIO) ---
class ClienteConfig(Base):
    __tablename__ = 'cliente_configs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('usuarios.id')) # Dono do perfil
    
    nome_perfil = Column(String)
    palavras_chave = Column(Text)
    palavras_negativas = Column(Text)
    
    # Relação opcional para facilitar query
    usuario = relationship("Usuario")

# --- MATCHES (VINCULADOS AO USUÁRIO PARA FILTRAGEM RÁPIDA) ---
class OportunidadeMatch(Base):
    __tablename__ = 'oportunidades_matches'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('usuarios.id')) # Quem deve ver isso?
    
    licitacao_id = Column(Integer)
    item_id = Column(Integer)
    perfil_cliente = Column(String)
    palavra_encontrada = Column(String)
    valor_estimado = Column(Float)
    quantidade = Column(Float)
    data_abertura = Column(DateTime, nullable=True)
    data_encerramento = Column(DateTime, nullable=True)
    link_pncp = Column(String)
    data_match = Column(DateTime, default=datetime.now)


# --- DEMAIS TABELAS (RAW e ITENS) ---
class LicitacaoRaw(Base):
    __tablename__ = 'licitacoes_raw'
    id = Column(Integer, primary_key=True)
    pncp_id = Column(String, unique=True)
    conteudo_json = Column(JSONB)
    objeto = Column(Text, nullable=True) 
    data_publicacao = Column(DateTime, nullable=True)
    codigo_modalidade = Column(Integer, nullable=True)
    itens = relationship("LicitacaoItem", back_populates="licitacao_raw") 

class LicitacaoItem(Base):
    __tablename__ = 'licitacoes_itens'
    id = Column(Integer, primary_key=True)
    licitacao_id = Column(Integer, ForeignKey('licitacoes_raw.id'))
    descricao = Column(String)
    quantidade = Column(Float, default=0.0)
    valor_unitario = Column(Float, default=0.0)
    
    # 2. Relação principal para Raw (Objeto Único)
    licitacao_raw = relationship("LicitacaoRaw", back_populates="itens") 
    
    # 3. Relação para Acompanhamento
    acompanhamentos = relationship("Acompanhamento", back_populates="item_detalhes")


# --- TABELA DE RASTREAMENTO: ACOMPANHAMENTO (ADICIONADO) ---
class Acompanhamento(Base):
    __tablename__ = 'acompanhamento'

    id = Column(Integer, primary_key=True, index=True)
    
    # Relação com o usuário
    user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    
    # Relação com o Item de Coleta
    item_id = Column(Integer, ForeignKey('licitacoes_itens.id'), nullable=False)
    
    data_acompanhamento = Column(DateTime, default=datetime.utcnow)

    # Garante que um usuário acompanhe um item apenas uma vez
    __table_args__ = (
        UniqueConstraint('user_id', 'item_id', name='uq_user_item_acompanhamento'),
    )

    # Relacionamentos para JOINs eficientes:
    item_detalhes = relationship("LicitacaoItem", back_populates="acompanhamentos") 
    usuario = relationship("Usuario")