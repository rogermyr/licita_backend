# app/db/utils.py
import unicodedata


def remover_acentos(texto: str) -> str:
    """Normaliza e remove acentos de uma string, convertendo para minúsculas."""
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', texto)
                      if unicodedata.category(c) != 'Mn').lower()