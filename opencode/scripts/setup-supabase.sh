#!/bin/bash
# FVS7 Agency - Setup do Supabase
# Inicializa o schema do banco de dados

set -euo pipefail

source ~/.config/opencode/.env 2>/dev/null || {
    echo "Arquivo .env nao encontrado em ~/.config/opencode/.env"
    exit 1
}

SCHEMA_FILE="$HOME/Documents/schema.sql"

if [ ! -f "$SCHEMA_FILE" ]; then
    echo "Schema nao encontrado em $SCHEMA_FILE"
    exit 1
fi

echo "Executando schema no Supabase..."
psql "$DATABASE_URL" -f "$SCHEMA_FILE"

echo "Schema criado com sucesso!"
