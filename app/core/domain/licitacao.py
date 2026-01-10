from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Licitacao:
    # 1. CAMPOS OBRIGATÓRIOS / SEM VALOR PADRÃO
    id_externo: str
    fonte: str
    objeto: str
    status_acompanhamento: str
    
    # *** ESTE CAMPO ESTAVA FALTANDO OU FOI OMITIDO NO DATACLASS ***
    user_id: int 
    
    # 2. CAMPOS OPCIONAIS / COM VALOR PADRÃO
    id_interno: Optional[int] = None 
    data_encerramento: Optional[datetime] = None
    valor_estimado: Optional[float] = None
    link_pncp: Optional[str] = None
    anotacoes: Optional[str] = None
    data_cadastro: Optional[datetime] = None
    
    # Factory Method (Certifique-se que o construtor abaixo usa user_id)
    @classmethod
    def criar_novo_acompanhamento(cls, 
                                id_externo: str, 
                                fonte: str, 
                                objeto: str, 
                                data_encerramento: Optional[datetime],
                                valor_estimado: Optional[float],
                                link_pncp: Optional[str],
                                user_id: int) -> 'Licitacao': # User_id no parâmetro
        
        return cls(
            id_externo=id_externo,
            fonte=fonte,
            objeto=objeto,
            status_acompanhamento="EM_ACOMPANHAMENTO",
            data_encerramento=data_encerramento,
            valor_estimado=valor_estimado,
            link_pncp=link_pncp,
            data_cadastro=datetime.now(),
            user_id=user_id # User_id no construtor
        )

    def alterar_status(self, novo_status: str):
        # Regra de negócio: Validação de transição de status
        if novo_status not in ["EM_ACOMPANHAMENTO", "SUSPENSA", "GANHA", "PERDIDA", "CANCELADA"]:
            raise ValueError(f"Status inválido: {novo_status}")
        self.status_acompanhamento = novo_status