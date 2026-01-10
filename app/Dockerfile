# Dockerfile
# Usamos a base 'slim' para ser pequena.

FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app
COPY requirements.txt .

# --------------------------------------------------------------------------------
# ETAPA CRÍTICA: Instala ferramentas de construção e dependências nativas
# Usamos o '&' e '&&' para garantir que tudo ocorra em uma única camada.
# --------------------------------------------------------------------------------
RUN apt-get update && \
    apt-get install -y netcat-openbsd build-essential libpq-dev && \
    # Limpa o cache do apt para reduzir o tamanho da imagem
    rm -rf /var/lib/apt/lists/*

# Instala as dependências Python
# Requisito: uvicorn[standard] e gunicorn devem estar em requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# --------------------------------------------------------------------------------

# ... (Seus passos anteriores: FROM, WORKDIR, COPY requirements, RUN apt-get, RUN pip install) ...

COPY . .

# Copia o script de entrypoint e o torna executável
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8000

# Define o ENTRYPOINT para rodar o script
ENTRYPOINT ["entrypoint.sh"]

CMD ["python", "-m", "gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "-w", "4", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "app.main:app"]