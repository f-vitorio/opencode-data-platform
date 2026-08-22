#!/bin/bash
# FVS7 Agency - Sincronizacao markdown <-> Supabase
# Sincroniza clientes entre arquivos .md e o banco

set -euo pipefail

source ~/.config/opencode/.env 2>/dev/null || {
    echo "Arquivo .env nao encontrado"
    exit 1
}

CLIENTS_DIR="$HOME/.config/opencode/clients"
mkdir -p "$CLIENTS_DIR"

echo "=== Sincronizacao Markdown <-> Supabase ==="

# 1. Listar clientes no banco
echo "Consultando banco..."
BANK_SLUGS=$(psql "$DATABASE_URL" -t -A -c "
    SELECT slug FROM clients WHERE is_active = true;
" 2>/dev/null)

# 2. Listar arquivos markdown
echo "Verificando arquivos markdown..."
MD_FILES=$(ls "$CLIENTS_DIR"/*.md 2>/dev/null || true)

# 3. Sync: banco -> markdown (exportar clientes sem arquivo)
for SLUG in $BANK_SLUGS; do
    if [ ! -f "$CLIENTS_DIR/$SLUG.md" ]; then
        echo "Exportando $SLUG do banco..."
        # O agente deve usar agency db export $SLUG
        psql "$DATABASE_URL" -c "
            SELECT * FROM clients WHERE slug = '$SLUG' AND is_active = true;
        " -t -A 2>/dev/null
    fi
done

# 4. Sync: markdown -> banco (importar arquivos novos)
for FILE in $MD_FILES; do
    BASENAME=$(basename "$FILE" .md)
    EXISTS=$(psql "$DATABASE_URL" -t -A -c "
        SELECT COUNT(*) FROM clients WHERE slug = '$BASENAME';
    " 2>/dev/null)
    
    if [ "$EXISTS" = "0" ]; then
        echo "Arquivo $BASENAME.md nao existe no banco - importar com agency db import $FILE"
    fi
done

echo "Sincronizacao concluida!"
