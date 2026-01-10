# app/services/search_processor.py
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional # MODIFICADO: Adicionado Optional
from sqlalchemy.orm import Session
from schemas.schemas import MatchResponse 
import unidecode 
import logging

logger = logging.getLogger(__name__)

# --- UTILITÁRIOS ---

def remover_acentos(text_val: str) -> str:
    if not text_val: return ""
    return unidecode.unidecode(text_val).lower()

def _gerar_link_pncp(identificador: str) -> str:
    try:
        partes = identificador.replace('-', '/').split('/')
        cnpj = partes[0]
        seq = partes[2]
        ano = partes[3]
        return f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{seq}"
    except Exception:
        return "https://pncp.gov.br/app/editais/"

# --- PROCESSAMENTO PRINCIPAL ---

def _format_silver_row_to_match(
    row: Any, 
    chaves_normalizadas_map: List[Tuple[str, str]]
) -> Dict[str, Any] | None:
    """
    Transforma uma linha da camada SILVER em um dicionário compatível com MatchResponse.
    """
    
    # 1. VALIDAÇÃO DE PRECISÃO (Substring Match)
    desc_norm = remover_acentos(row.descricao)
    
    # Se não houver chaves para validar (caso raro), permite passar
    if not chaves_normalizadas_map:
        termos_encontrados = ["Busca Global"]
    else:
        # Filtra quais termos do mapa estão presentes na descrição do item
        termos_encontrados = [
            orig for orig, norm in chaves_normalizadas_map 
            if norm in desc_norm
        ]
    
    # Se o item não contém nenhum dos termos buscados, ele é descartado pelo processador
    if not termos_encontrados:
        return None 
        
    local = f"{row.municipio_nome}/{row.uf_sigla}" if row.municipio_nome else row.uf_sigla

    return {
        "id": row.item_id,
        "perfil_cliente": "Busca Personalizada" if not chaves_normalizadas_map else "Múltiplos Perfis",
        "palavra_encontrada": row.descricao,
        "termo_chave": ", ".join(termos_encontrados),
        "objeto_licitacao": row.objeto,
        "valor_unitario": float(row.valor_unitario or 0),
        "quantidade": float(row.quantidade or 0), 
        "valor_total_item": float(row.valor_total_item or 0),
        "valor_estimado": float(row.valor_total_item or 0), 
        "link_pncp": _gerar_link_pncp(row.licitacao_identificador),
        "data_match": row.data_publicacao,
        "data_encerramento": row.data_encerramento,
        "local": local,
        "modalidade_codigo": str(row.modalidade_nome)
    }

# MODIFICADO: Adicionado parâmetro custom_keywords
def process_search_results(
    db: Session, 
    perfis: List[Any], 
    resultados_brutos: List[Any],
    custom_keywords: Optional[str] = None # // NOVO
) -> List[MatchResponse]:
    """
    Orquestra a transformação de resultados SQL para a lista final de Matches.
    """
    lista_final: List[MatchResponse] = []
    ids_vistos = set()

    # --- LÓGICA DE DEFINIÇÃO DE CHAVES PARA VALIDAÇÃO ---
    chaves_brutas = []
    
    # // NOVO: Se houver busca personalizada, ela define as chaves de validação
    if custom_keywords and custom_keywords.strip():
        for k in custom_keywords.split(","):
            if k.strip():
                chaves_brutas.append(k.strip())
        logger.info(f"🎯 Processor: Validando resultados contra termos Ad-hoc: {chaves_brutas}")
    else:
        # Caso contrário, usa as palavras do perfil (comportamento padrão)
        for p in perfis:
            kw = p.palavras_chave or ""
            for k in kw.split(","):
                if k.strip():
                    chaves_brutas.append(k.strip())
    
    # Remove duplicatas e normaliza para comparação
    chaves_map = [(c, remover_acentos(c)) for c in set(chaves_brutas)]
    
    logger.info(f"🚀 Silver Processor: Formatando {len(resultados_brutos)} itens.")

    for row in resultados_brutos:
        if row.item_id in ids_vistos: continue

        try:
            # Passa o mapa de chaves (que agora pode ser do perfil ou ad-hoc)
            dados = _format_silver_row_to_match(row, chaves_map)
            
            if dados:
                lista_final.append(MatchResponse(**dados))
                ids_vistos.add(row.item_id)
                
        except Exception as e:
            logger.error(f"❌ Erro ao formatar item {getattr(row, 'item_id', 'N/A')}: {e}")
            continue
            
    return lista_final