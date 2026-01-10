# app/services/acompanhamento_processor.py

from typing import List, Dict, Any
import logging
from schemas.schemas import ItemAcompanhadoResponse

logger = logging.getLogger(__name__)

def process_acompanhamento_list(acompanhamentos_brutos: List[Any]) -> List[ItemAcompanhadoResponse]:
    """
    MODIFICADO: Processa uma lista de Rows (SQL Raw) para o formato ItemAcompanhadoResponse.
    Agora o processador é leve pois o SQL já entregou os dados prontos.
    """
    lista_final: List[ItemAcompanhadoResponse] = []
    
    logger.info(f"PROCESSAMENTO ACOMPANHAMENTO: Formatando {len(acompanhamentos_brutos)} registros vindos do SQL.")

    for row in acompanhamentos_brutos:
        try:
            # O SQL Raw já entrega os nomes das colunas idênticos ao que o Schema espera.
            # Convertemos a Row do SQLAlchemy em um dicionário.
            dados = dict(row._mapping)

            # Ajustes de compatibilidade final entre Backend e Frontend
            item_formatado = {
                "id": dados.get("id"),
                "item_id": dados.get("item_id"),
                "palavra_encontrada": dados.get("palavra_encontrada"),
                "termo_chave": dados.get("termo_chave", "Acompanhado"),
                "objeto_licitacao": dados.get("objeto_licitacao"),
                "quantidade": dados.get("quantidade"),
                "valor_unitario": dados.get("valor_unitario"),
                "valor_estimado": dados.get("valor_estimado"), # Fallback
                "valor_total_item": dados.get("valor_total_item"),
                "local": dados.get("local"),
                "data_match": dados.get("data_match"),
                "data_encerramento": dados.get("data_encerramento"),
                "data_acompanhamento": dados.get("data_acompanhamento"),
                "modalidade_codigo": dados.get("modalidade_codigo"),
                "link_pncp": dados.get("link_pncp") or "#",
                "link_origem_bruto": dados.get("link_origem_bruto") or "#",
                "orgao_razao_social": dados.get("orgao_razao_social")
            }

            # Validação pelo Pydantic Schema
            lista_final.append(ItemAcompanhadoResponse(**item_formatado))

        except Exception as e:
            logger.error(f"❌ Erro ao formatar linha de acompanhamento: {e}")
            continue
            
    logger.info(f"PROCESSAMENTO ACOMPANHAMENTO: {len(lista_final)} itens prontos para o frontend.")
    return lista_final