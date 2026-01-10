# app/models/licitacao.py

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base 

# --- TABELA: DADOS BRUTOS DA LICITAÇÃO (RAW) ---
class LicitacaoRaw(Base):
    __tablename__ = 'licitacoes_raw'
    id = Column(Integer, primary_key=True)
    pncp_id = Column(String, unique=True)
    conteudo_json = Column(JSONB)
    objeto = Column(Text, nullable=True) 
    data_publicacao = Column(DateTime, nullable=True)
    codigo_modalidade = Column(Integer, nullable=True)
    
    itens = relationship("LicitacaoItem", back_populates="licitacao_raw") 

# --- TABELA: ITENS DA LICITAÇÃO ---
class LicitacaoItem(Base):
    __tablename__ = 'licitacoes_itens'
    id = Column(Integer, primary_key=True)
    
    licitacao_id = Column(Integer, ForeignKey('licitacoes_raw.id'))
    
    descricao = Column(String)
    quantidade = Column(Float, default=0.0)
    valor_unitario = Column(Float, default=0.0)
    
    licitacao_raw = relationship("LicitacaoRaw", back_populates="itens")
    
    # Relação para Acompanhamento (usada em tracking.py)
    acompanhamentos = relationship("Acompanhamento", back_populates="item_detalhes")