"""
Script para inicializar o banco de dados.
Cria todas as tabelas definidas nos modelos.
"""
from db.base import Base  
from db.session import engine 

# Importa todos os modelos para que sejam registrados no Base.metadata
# O ato de importar as classes é crucial para a descoberta de tabelas
from models import (
    Usuario, 
    ClienteConfig, 
    OportunidadeMatch, 
    LicitacaoRaw, 
    LicitacaoItem,
    Acompanhamento,
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