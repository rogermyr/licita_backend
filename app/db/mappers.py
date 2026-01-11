"""
Mappers para conversão entre entidades de domínio e modelos DB.
NOTA: Este arquivo está atualmente não utilizado no projeto.
Mantido para referência futura caso seja necessário.
"""
# app/db/mappers.py

# TODO: Este arquivo precisa ser atualizado quando o modelo DB correto for definido
# Atualmente, o projeto usa Acompanhamento em models/tracking.py em vez de LicitacaoDBModel

# Importa as classes das outras camadas para definir as assinaturas
from app.core.domain.licitacao import Licitacao

# NOTA: LicitacaoDBModel não existe mais - removido/refatorado
# from db.models.licitacao import LicitacaoDBModel

# Função desabilitada até que o modelo correto seja definido
def map_domain_to_db(domain_entity: Licitacao):
    """
    Converte uma Entidade de Domínio (Licitacao) para um Modelo ORM.
    
    NOTA: Esta função está desabilitada até que o modelo DB correto seja definido.
    O projeto atualmente usa Acompanhamento em models/tracking.py.
    """
    raise NotImplementedError(
        "Esta função precisa ser atualizada com o modelo DB correto. "
        "Atualmente, o projeto usa Acompanhamento em vez de LicitacaoDBModel."
    )

def map_db_to_domain(db_model) -> Licitacao:
    """
    Converte um Modelo ORM para uma Entidade de Domínio (Licitacao).
    
    NOTA: Esta função está desabilitada até que o modelo DB correto seja definido.
    """
    raise NotImplementedError(
        "Esta função precisa ser atualizada com o modelo DB correto. "
        "Atualmente, o projeto usa Acompanhamento em vez de LicitacaoDBModel."
    )