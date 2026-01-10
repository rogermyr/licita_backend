# app/models/base.py (OU mantenha em app/db/base.py se essa for a convenção)

from sqlalchemy.ext.declarative import declarative_base
from typing import Any

# Tipagem para a classe Base.
class CustomBase:
    __name__: str
    id: Any
    
# Cria o objeto Base que todos os modelos ORM devem herdar.
Base = declarative_base(cls=CustomBase)