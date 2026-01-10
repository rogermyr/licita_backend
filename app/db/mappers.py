# app/db/mappers.py

# Importa as classes das outras camadas para definir as assinaturas
from core.domain.licitacao import Licitacao
from db.models.licitacao import LicitacaoDBModel

def map_domain_to_db(domain_entity: Licitacao) -> LicitacaoDBModel:
    """
    Converte uma Entidade de Domínio (Licitacao) para um Modelo ORM (LicitacaoDBModel).
    """
    # A ID interna é preservada se existir (para atualizações)
    db_model = LicitacaoDBModel(
        id=domain_entity.id_interno, # Pode ser None
        id_externo=domain_entity.id_externo,
        fonte=domain_entity.fonte,
        objeto=domain_entity.objeto,
        status_acompanhamento=domain_entity.status_acompanhamento,
        data_encerramento=domain_entity.data_encerramento,
        user_id=domain_entity.user_id, 
        valor_estimado=domain_entity.valor_estimado,
        link_pncp=domain_entity.link_pncp,
        anotacoes=domain_entity.anotacoes,
        data_cadastro=domain_entity.data_cadastro
    )
    return db_model

def map_db_to_domain(db_model: LicitacaoDBModel) -> Licitacao:
    """
    Converte um Modelo ORM (LicitacaoDBModel) para uma Entidade de Domínio (Licitacao).
    """
    domain_entity = Licitacao(
        id_interno=db_model.id,
        id_externo=db_model.id_externo,
        fonte=db_model.fonte,
        objeto=db_model.objeto,
        status_acompanhamento=db_model.status_acompanhamento,
        data_encerramento=db_model.data_encerramento,
        valor_estimado=db_model.valor_estimado,
        link_pncp=db_model.link_pncp,
        anotacoes=db_model.anotacoes,
        data_cadastro=db_model.data_cadastro
    )
    return domain_entity