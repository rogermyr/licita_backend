from datetime import datetime
from typing import Optional, List

# Importações corrigidas:
from core.ports.repositorio_licitacoes import RepositorioLicitacoes 
from core.domain.licitacao import Licitacao 

class LicitacaoJaAcompanhadaError(Exception):
    pass


class CasoDeUsoAdicionarAcompanhamento:
    def __init__(self, repositorio: RepositorioLicitacoes):
        self._repositorio = repositorio

    # NOVO: user_id adicionado aos parâmetros de entrada
    def executar(self, id_match_externo: int, fonte: str, objeto: str, data_encerramento: datetime, valor_estimado: float, link_pncp: str, user_id: int) -> Licitacao:
        
        id_externo_str = str(id_match_externo)

        if self._repositorio.existe_por_id_externo(id_externo_str):
            raise LicitacaoJaAcompanhadaError(...)
            
        nova_licitacao = Licitacao.criar_novo_acompanhamento(
            id_externo=id_externo_str,
            fonte=fonte,
            objeto=objeto,
            data_encerramento=data_encerramento,
            valor_estimado=valor_estimado,
            link_pncp=link_pncp,
            user_id=user_id # FINALMENTE PASSANDO PARA O FACTORY METHOD
        )
        
        return self._repositorio.salvar(nova_licitacao)