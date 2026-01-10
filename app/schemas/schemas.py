# app/schemas/schemas.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any 
from datetime import datetime, date

# --- 1. SCHEMAS DE USUÁRIO ---

class UserCreate(BaseModel):
    username: str 
    password: str
    nome_completo: str
    telefone: str
    cpf: str
    cargo: str

class UserResponse(BaseModel):
    id: int
    username: str
    nome_completo: Optional[str] = None
    telefone: Optional[str] = None
    cpf: Optional[str] = None
    cargo: Optional[str] = None
    data_cadastro: Optional[datetime] = None 
    model_config = ConfigDict(from_attributes=True)


# --- 2. SCHEMAS DE PERFIS (CONFIGURAÇÃO DE BUSCA) ---

class PerfilSchema(BaseModel):
    nome_perfil: str
    palavras_chave: str
    palavras_negativas: Optional[str] = None 

class PerfilResponse(PerfilSchema):
    id: int
    model_config = ConfigDict(from_attributes=True)


# --- 3. SCHEMAS DE VARREDURA (REQUEST DO FRONTEND) ---

class VarreduraRequest(BaseModel):
    perfil_ids: List[int]
    # NOVO: Termos personalizados que substituem os do perfil
    custom_keywords: Optional[str] = None 
    
    filtro_uf: Optional[List[str]] = None
    filtro_modalidade: Optional[Any] = None
    apenas_me_epp: Optional[bool] = False
    valor_min: Optional[float] = None
    valor_max: Optional[float] = None

    limit: int = Field(default=50, gt=0, le=100)
    offset: int = Field(default=0, ge=0)
    last_valor_total: Optional[float] = None
    last_item_id: Optional[int] = None


# --- 4. SCHEMAS DE MATCH (RESPOSTA DA LICITAÇÃO) ---

class MatchResponse(BaseModel):
    id: int
    perfil_cliente: Optional[str] = "N/A"
    palavra_encontrada: str 
    termo_chave: Optional[str] = "N/A" 
    
    objeto_licitacao: str
    valor_estimado: Optional[float] = None
    quantidade: Optional[float] = None
    valor_unitario: Optional[float] = None 
    
    valor_total_item: Optional[float] = None 
    
    link_pncp: Optional[str] = "#" 
    data_match: datetime
    local: str
    modalidade_codigo: Optional[str] = None
    data_encerramento: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- 5. SCHEMAS DE PAGINAÇÃO (METADADOS) ---

class CursorInfo(BaseModel):
    next_last_valor_total: Optional[float] = None
    next_last_item_id: Optional[int] = None

class VarreduraPaginadaResponse(BaseModel):
    total_items: int
    limit: int
    offset: int
    resultados: List[MatchResponse]
    cursor: Optional[CursorInfo] = None 


# --- 6. SCHEMAS DE ACOMPANHAMENTO (TRACKING) ---

class AcompanhamentoAction(BaseModel):
    item_id: int
    acompanhar: bool = True

class ItemAcompanhadoResponse(MatchResponse):
    data_acompanhamento: datetime
    item_id: Optional[int] = None 
    
    model_config = ConfigDict(from_attributes=True)


# --- 7. SISTEMAS ---

class SistemaResponse(BaseModel): 
    nome: str
    model_config = ConfigDict(from_attributes=True)