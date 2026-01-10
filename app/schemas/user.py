from pydantic import BaseModel, Field, ConfigDict # NOVO: Importamos Field e ConfigDict
from typing import Optional
# Importamos datetime, se data_cadastro for usado no modelo Usuario (Boa Prática)
from datetime import datetime 


# Schema para a resposta (exclui a senha hash)
class UserResponse(BaseModel):
    id: int
    
    # CRÍTICO 1: Usamos alias para mapear 'username' do DB para 'email' na API (Conforme UX/padrão)
    # Se você preferir manter o campo como 'username' na resposta JSON, remova o Field(alias="...").
    # Mantenho o alias pois o token JWT usa "sub" que geralmente é email.
    username: str
    
    # CRÍTICO 2: Tornamos os campos obrigatórios opcionais para aceitar NULL do DB e prevenir ResponseValidationError
    nome_completo: Optional[str] = None # MODIFICADO
    telefone: Optional[str] = None      # MODIFICADO
    cpf: Optional[str] = None           # MODIFICADO
    
    # Cargo já era Optional
    cargo: Optional[str] = None
    
    # Adicionando data_cadastro como Optional (assumindo que existe no ORM)
    data_cadastro: Optional[datetime] = None 
    
    # Configuração Pydantic V2 (Substitui 'class Config:')
    model_config = ConfigDict(
        from_attributes=True, 
        populate_by_name=True 
    )


# Schema para a atualização de dados (senha é separada)
class UserUpdate(BaseModel):
    nome_completo: Optional[str] = None
    telefone: Optional[str] = None
    cpf: Optional[str] = None
    cargo: Optional[str] = None
    
    # Usamos ConfigDict para UserUpdate também, para garantir compatibilidade
    model_config = ConfigDict(from_attributes=True)