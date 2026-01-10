# app/crud/acompanhamento_logic.py

from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def toggle_acompanhamento(db: Session, user_id: int, item_id: int, should_acompanhar: bool) -> bool:
    """
    Marca ou desmarca um item de licitação para acompanhamento.
    """
    # Verifica se já existe o vínculo
    query_check_existing = text("SELECT 1 FROM acompanhamento WHERE user_id = :u AND item_id = :i")
    existing = db.execute(query_check_existing, {"u": user_id, "i": item_id}).first()

    if should_acompanhar:
        if existing:
            return True 
        
        try:
            # 1. Verifica se o item existe na tabela SILVER
            query_check_item = text("SELECT 1 FROM silver_itens WHERE id = :id LIMIT 1")
            if not db.execute(query_check_item, {"id": item_id}).first():
                logger.error(f"❌ Item ID {item_id} não existe na tabela silver_itens.")
                return False

            # 2. Insere usando SQL Raw para evitar conflitos de mapeamento ORM
            query_insert = text("""
                INSERT INTO acompanhamento (user_id, item_id, data_acompanhamento) 
                VALUES (:u, :i, NOW())
            """)
            db.execute(query_insert, {"u": user_id, "i": item_id})
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Falha crítica ao inserir acompanhamento: {e}")
            return False
            
    else: # Desmarcar
        try:
            query_delete = text("DELETE FROM acompanhamento WHERE user_id = :u AND item_id = :i")
            db.execute(query_delete, {"u": user_id, "i": item_id})
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Erro ao remover acompanhamento: {e}")
            return False
            

def get_acompanhamentos_by_user(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 50,
    sort_by: str = "data_encerramento",
    order: str = "asc"
):
    """
    Busca os registros de acompanhamento corrigindo o nome da tabela para o singular 'acompanhamento'.
    """
    
    VALOR_TOTAL_EXPR = "(COALESCE(i.valor_unitario_estimado, 0) * COALESCE(i.quantidade, 0))"

    # Mapeamento de ordenação
    order_col = "l.data_encerramento" if sort_by == "data_encerramento" else "a.data_acompanhamento"
    order_direction = f"{order.upper()} NULLS LAST"

    # MODIFICADO: Alterado de 'acompanhamentos' para 'acompanhamento' (singular)
    # MODIFICADO: Confirmado o join com 'silver_itens' e 'silver_licitacoes'
    query_sql = f"""
        SELECT 
            i.id as id, 
            i.id as item_id,
            i.quantidade,
            i.valor_unitario_estimado as valor_unitario,
            i.valor_unitario_estimado as valor_estimado,
            {VALOR_TOTAL_EXPR} as valor_total_item,
            i.descricao as palavra_encontrada, 
            l.municipio_nome || '/' || l.uf_sigla as local,
            l.data_encerramento,
            l.data_publicacao as data_match,
            l.modalidade_nome as modalidade_codigo,
            l.objeto_compra as objeto_licitacao,
            COALESCE(l.link_sistema_origem, '#') as link_pncp,
            a.data_acompanhamento as data_acompanhamento
        FROM acompanhamento a -- TABELA CORRIGIDA PARA O SINGULAR
        JOIN silver_itens i ON a.item_id = i.id
        LEFT JOIN silver_licitacoes l ON i.licitacao_identificador = l.identificador_pncp
        WHERE a.user_id = :user_id
        ORDER BY {order_col} {order_direction}
        LIMIT :limit OFFSET :skip
    """

    params = {
        "user_id": user_id,
        "limit": limit,
        "skip": skip
    }

    try:
        # Execução do SQL Raw
        return db.execute(text(query_sql), params).all()
    except Exception as e:
        logger.error(f"❌ Erro ao buscar acompanhamentos (SQL Raw): {e}")
        return []

def check_item_is_acompanhado(db: Session, user_id: int, item_id: int) -> bool:
    """Verifica se um item está em acompanhamento."""
    # MODIFICADO: Corrigido nome da tabela aqui também
    query = text("SELECT 1 FROM acompanhamento WHERE user_id = :u AND item_id = :i LIMIT 1")
    return db.execute(query, {"u": user_id, "i": item_id}).first() is not None