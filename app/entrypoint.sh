#!/bin/bash

# Define a função de espera pelo DB
wait_for_db() {
  echo "Aguardando o PostgreSQL em ${DB_HOST}:${DB_PORT}..."

  # Loop de espera. Note que estamos usando 'db' como host.
  # Você deve garantir que 'db' é o nome do host correto (service name).
  while ! nc -z db 5432; do
    echo "PostgreSQL ainda não está pronto. Dormindo por 1 segundo..."
    sleep 1
  done

  echo "PostgreSQL está pronto!"
}

# 1. Espera pelo banco de dados
wait_for_db

# 2. Executa migrações do Alembic
echo "Executando migrações..."
python -m alembic upgrade head

# 3. Executa o comando principal (o CMD que vem depois)
exec "$@"