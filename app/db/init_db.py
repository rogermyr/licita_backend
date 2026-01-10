import os
import sys
# Adiciona o diretório raiz do projeto ao path para que imports como 'from app.db...' funcionem
# Isso resolve o problema de execução de módulo que você teve inicialmente.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.base import Base  
from app.db.session import engine 

# -------------------------------------------------------------
# 1. IMPORTAÇÃO DE TODOS OS MODELOS PARA REGISTRAR NO Base.metadata
# O ATO DE IMPORTAR AS CLASSES É CRUCIAL PARA A DESCOBERTA DE TABELAS
# -------------------------------------------------------------

# Importa o modelo que gera a tabela 'licitacoes_acompanhamento'
# Garanta que LicitacaoDBModel herde de app.db.base.Base
from db.models.licitacao import LicitacaoDBModel 

# Importa todos os modelos definidos no seu arquivo de modelos do usuário
# Garanta que todos estes modelos herdem de app.db.base.Base
from models import (
    Usuario, 
    ClienteConfig, 
    OportunidadeMatch, 
    LicitacaoRaw, 
    LicitacaoItem
)

# -------------------------------------------------------------

def initialize_database():
    """
    Função principal para criar todas as tabelas registradas no Base.metadata.
    """
    print("Iniciando a criação das tabelas no banco de dados...")
    
    # OPCIONAL: Se precisar limpar todas as tabelas existentes (uso em desenvolvimento)
    # print("Aviso: Dropando todas as tabelas (Se descomentado)...")
    # Base.metadata.drop_all(bind=engine)
    
    # Cria todas as tabelas (incluindo 'usuarios' e 'licitacoes_acompanhamento')
    # Como todos os modelos foram importados, o SQLAlchemy pode resolver a Foreign Key.
    Base.metadata.create_all(bind=engine)
    print("Criação de tabelas concluída com sucesso.")

if __name__ == "__main__":
    # Garante que o script só execute quando chamado diretamente
    initialize_database()