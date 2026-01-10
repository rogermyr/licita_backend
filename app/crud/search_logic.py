# app/crud/search_logic.py
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Any, Tuple, Dict
import logging
import unidecode 

logger = logging.getLogger(__name__)

# Mapeamento de IDs para nomes parciais no banco de dados
MODALIDADES_NOME_MAP = {
    "1": "Leilão",
    "2": "Diálogo Competitivo",
    "3": "Concurso",
    "4": "Concorrência",
    "5": "Concorrência",
    "6": "Pregão",
    "7": "Pregão",
    "8": "Dispensa",        
    "9": "Inexigibilidade", 
    "10": "Manifestação",
    "11": "Pré-qualificação",
    "12": "Credenciamento",
    "13": "Leilão",
    "14": "Inaplicabilidade",
    "15": "Chamada pública"
}

def remover_acentos(text_val: str) -> str:
    if not text_val: return ""
    return unidecode.unidecode(text_val).lower()

def format_list_for_sql_in(items: List[Any]) -> str:
    valid_items = [str(item).replace("'", "''") for item in items if item]
    if not valid_items:
        return "NULL"
    return ', '.join("'{0}'".format(item) for item in valid_items)

def build_and_execute_search_query(
    db: Session, 
    perfis: List[Any], 
    dados: Any
) -> Tuple[List[Any], int]:
    
    # 1. PRÉ-PROCESSAMENTO DE TERMOS
    termos_inclusao = []
    termos_exclusao = []

    # // MODIFICADO: Lógica de Isolamento Total
    # Verificamos se o usuário forneceu termos de busca personalizados
    possui_custom = bool(getattr(dados, 'custom_keywords', None) and dados.custom_keywords.strip())

    if possui_custom:
        # --- MODO AD-HOC (BUSCA PURA) ---
        # Ignora inclusões e exclusões do perfil para permitir teste livre
        logger.info(f"⚡ MODO AD-HOC ATIVO: Ignorando filtros de perfil para: {dados.custom_keywords}")
        for k in dados.custom_keywords.split(","):
            if k.strip():
                termos_inclusao.append(remover_acentos(k.strip()).replace(" ", " & "))
        
        # Garantimos que a lista de exclusão esteja vazia para este modo
        termos_exclusao = []
    else:
        # --- MODO PERFIL (PADRÃO) ---
        # Usa as palavras de inclusão e negativa dos perfis selecionados no banco
        for p in perfis:
            # Processa palavras-chave de inclusão
            kw = p.palavras_chave or ""
            for k in kw.split(","):
                if k.strip():
                    termos_inclusao.append(remover_acentos(k.strip()).replace(" ", " & "))
            
            # Processa palavras-chave negativas (exclusão)
            nw = p.palavras_negativas or ""
            for k in nw.split(","):
                if k.strip():
                    termos_exclusao.append(remover_acentos(k.strip()).replace(" ", " & "))
                
    sql_params: Dict[str, Any] = {
        "limit_val": int(dados.limit)
    }
    
    VALOR_TOTAL_EXPR = "(COALESCE(i.valor_unitario_estimado, 0) * COALESCE(i.quantidade, 0))"

    # ---------------------------------------------------------------------
    # 2. CONSTRUÇÃO DOS FILTROS
    # ---------------------------------------------------------------------
    
    # Filtro Textual de Inclusão
    fts_sql = ""
    if termos_inclusao:
        sql_params["ts_inc"] = " | ".join(termos_inclusao)
        fts_sql = "to_tsvector('portuguese', i.descricao) @@ to_tsquery('portuguese', :ts_inc)" 

    # Filtro Textual de Exclusão (Só existirá se não for modo Ad-hoc)
    neg_sql = ""
    if termos_exclusao:
        sql_params["ts_exc"] = " | ".join(termos_exclusao)
        neg_sql = "NOT (to_tsvector('portuguese', i.descricao) @@ to_tsquery('portuguese', :ts_exc))"
    
    # Filtro UF
    uf_sql = ""
    if dados.filtro_uf and len(dados.filtro_uf) > 0:
        ufs_limpas = [uf.upper().strip() for uf in dados.filtro_uf if uf]
        if ufs_limpas:
            uf_sql = f"TRIM(UPPER(l.uf_sigla)) IN ({format_list_for_sql_in(ufs_limpas)})"
        
    # Filtro Modalidade
    mod_sql = ""
    raw_mod = dados.filtro_modalidade
    if raw_mod:
        m_id = str(raw_mod[0]) if isinstance(raw_mod, list) and len(raw_mod) > 0 else str(raw_mod)
        if m_id and m_id != "todos":
            nome_db = MODALIDADES_NOME_MAP.get(m_id)
            if nome_db:
                sql_params["mod_nome"] = f"%{nome_db.upper()}%"
                mod_sql = "TRIM(UPPER(l.modalidade_nome)) LIKE :mod_nome"

    # Filtros de Valor
    val_min_sql = ""
    if dados.valor_min is not None and dados.valor_min != "":
        sql_params["v_min"] = float(dados.valor_min)
        val_min_sql = f"{VALOR_TOTAL_EXPR} >= :v_min"

    # Filtro de Valor Máximo
    val_max_sql = ""
    if dados.valor_max is not None and dados.valor_max != "":
        sql_params["v_max"] = float(dados.valor_max)
        val_max_sql = f"{VALOR_TOTAL_EXPR} <= :v_max"

    # Filtro de Validade
    validade_sql = "(l.data_encerramento >= CURRENT_DATE OR l.data_encerramento IS NULL)"

    # Pagination (Keyset)
    keyset_sql = ""
    if dados.last_valor_total is not None and dados.last_item_id is not None:
        keyset_sql = f"AND ({VALOR_TOTAL_EXPR} < :l_val OR ({VALOR_TOTAL_EXPR} = :l_val AND i.id < :l_id))"
        sql_params["l_val"] = float(dados.last_valor_total)
        sql_params["l_id"] = int(dados.last_item_id)

    # ---------------------------------------------------------------------
    # 3. MONTAGEM E EXECUÇÃO
    # ---------------------------------------------------------------------
    
    filters = [
        fts_sql, neg_sql, uf_sql, mod_sql, 
        validade_sql, val_min_sql, val_max_sql
    ]
    active_filters = [f for f in filters if f]
    where_clause = "WHERE " + " AND ".join(active_filters) if active_filters else "WHERE 1=1"

    query_sql = f"""
        SELECT DISTINCT
            i.id as item_id, i.licitacao_identificador, i.descricao, i.quantidade,
            i.valor_unitario_estimado as valor_unitario,
            {VALOR_TOTAL_EXPR} as valor_total_item, 
            l.objeto_compra as objeto, l.data_publicacao, l.data_encerramento,
            l.modalidade_nome, l.municipio_nome, l.uf_sigla, l.orgao_razao_social,
            l.link_sistema_origem as link_origem_bruto
        FROM silver_itens i
        JOIN silver_licitacoes l ON i.licitacao_identificador = l.identificador_pncp
        {where_clause}
        {keyset_sql}
        ORDER BY valor_total_item DESC, i.id DESC 
        LIMIT :limit_val 
    """ 

    try:
        resultados = db.execute(text(query_sql), sql_params).all()
        return resultados, 0
    except Exception as e:
        logger.error(f"❌ Erro na query Silver: {e}")
        return [], 0