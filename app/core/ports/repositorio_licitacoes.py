from abc import ABC, abstractmethod
from typing import List, Optional

# Importamos a Entidade que definimos no Arquivo 1
from app.core.domain.licitacao import Licitacao 

class RepositorioLicitacoes(ABC):
    """Interface (Port) definindo o contrato de persistência para o Core."""
    
    @abstractmethod
    def salvar(self, licitacao: Licitacao) -> Licitacao:
        """Salva ou atualiza uma licitação na base de dados."""
        pass
        
    @abstractmethod
    def buscar_por_id_externo(self, id_externo: str) -> Optional[Licitacao]:
        """Busca uma licitação pelo ID externo (ID do Match)."""
        pass
        
    @abstractmethod
    def existe_por_id_externo(self, id_externo: str) -> bool:
        """Verifica se uma licitação com o ID externo já existe."""
        pass
        
    @abstractmethod
    def buscar_todos(self) -> List[Licitacao]:
        """Lista todas as licitações em acompanhamento."""
        pass