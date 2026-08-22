#!/bin/bash
# FVS7 Agency - Keepalive do Supabase
# Evita pausa apos 7 dias de inatividade

set -euo pipefail

source ~/.config/opencode/.env 2>/dev/null || {
    echo "Arquivo .env nao encontrado"
    exit 1
}

echo "Enviando keepalive para Supabase..."

RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    "$SUPABASE_URL/rest/v1/" \
    -H "apikey: $SUPABASE_ANON_KEY" \
    -H "Authorization: Bearer $SUPABASE_ANON_KEY")

if [ "$RESPONSE" = "200" ]; then
    echo "Supabase ativo (HTTP $RESPONSE)"
    echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
else
    echo "ERRO: Supabase retornou HTTP $RESPONSE"
    exit 1
fi
