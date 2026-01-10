# app/models/tracking.py

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint 
from datetime import datetime
from .base import Base # Importa a base do nosso novo módulo

# --- TABELA DE RASTREAMENTO: ACOMPANHAMENTO ---
class Acompanhamento(Base):
    __tablename__ = 'acompanhamento'

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key para Usuario e LicitacaoItem
    user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('licitacoes_itens.id'), nullable=False)
    
    data_acompanhamento = Column(DateTime, default=datetime.utcnow)

    # Garante que um usuário acompanhe um item apenas uma vez
    __table_args__ = (
        UniqueConstraint('user_id', 'item_id', name='uq_user_item_acompanhamento'),
    )

    # Relacionamentos para JOINs eficientes:
    # item_detalhes: Referencia o LicitacaoItem (definido em licitacao.py)
    item_detalhes = relationship("LicitacaoItem", back_populates="acompanhamentos") 
    
    # usuario: Referencia o Usuario (definido em user.py)
    usuario = relationship("Usuario")

# --- TABELA: MATCHES (VINCULADOS AO USUÁRIO) ---
class OportunidadeMatch(Base):
    __tablename__ = 'oportunidades_matches'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('usuarios.id')) # Quem deve ver isso?
    
    # Campos que se referem aos itens da licitação (sem Foreign Key rígida)
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

    # Relacionamento (opcional, mas recomendado)
    usuario = relationship("Usuario")