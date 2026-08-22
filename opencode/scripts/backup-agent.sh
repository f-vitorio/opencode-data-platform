#!/bin/bash
# ============================================
# FVS7 Agency - Script de Backup
# Backup de configs, skills e knowledge → GitHub
# ============================================

set -euo pipefail

# Carregar variáveis de ambiente
source ~/.config/opencode/.env 2>/dev/null || {
    echo "❌ Arquivo .env não encontrado em ~/.config/opencode/.env"
    exit 1
}

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
REPO_DIR="$HOME/.config/opencode-backup"
BACKUP_LOG="/tmp/fvs7-backup.log"

echo "🔄 Iniciando backup: $TIMESTAMP"

# 1. Verificar se o repositório existe
if [ ! -d "$REPO_DIR/.git" ]; then
    echo "📦 Clonando repositório de backup..."
    git clone git@github.com:f-vitorio/opencode-data-platform.git "$REPO_DIR"
fi

cd "$REPO_DIR"

# 2. Copiar configurações do OpenCode
echo "📋 Copiando configurações..."
rsync -av --delete \
    --exclude='node_modules' \
    --exclude='*.backup-*' \
    --exclude='session-env' \
    --exclude='cache' \
    --exclude='telemetry' \
    --exclude='.env' \
    --exclude='package-lock.json' \
    ~/.config/opencode/ "$REPO_DIR/opencode/" 2>/dev/null

# 3. Copiar knowledge base do Claude
echo "📚 Copiando knowledge base..."
mkdir -p "$REPO_DIR/claude"
rsync -av ~/.claude/AGENCY-KNOWLEDGE.md "$REPO_DIR/claude/" 2>/dev/null || true
rsync -av ~/.claude/CLAUDE.md "$REPO_DIR/claude/" 2>/dev/null || true
rsync -av --delete ~/.claude/agency-system/ "$REPO_DIR/claude/agency-system/" 2>/dev/null || true

# 4. Copiar skills do Claude (se existirem)
if [ -d ~/.claude/skills ]; then
    rsync -av --delete ~/.claude/skills/ "$REPO_DIR/claude/skills/" 2>/dev/null || true
fi

# 5. Copiar agency knowledge
echo "🏢 Copiando agency knowledge..."
mkdir -p "$REPO_DIR/agency"
rsync -av --delete ~/.agency/knowledge/ "$REPO_DIR/agency/knowledge/" 2>/dev/null || true
rsync -av --delete ~/.agency/sources/ "$REPO_DIR/agency/sources/" 2>/dev/null || true

# 6. Criar manifest de backup
cat > "$REPO_DIR/BACKUP_MANIFEST.md" << EOF
# Backup Manifest

- **Data:** $TIMESTAMP
- **Hostname:** $(hostname)
- **User:** $(whoami)

## Arquivos incluídos

### OpenCode Config
- AGENTS.md
- opencode.jsonc
- company-profile/
- skills/ (11 skills)
- agents/ (3 agentes)
- scripts/

### Claude Config
- AGENCY-KNOWLEDGE.md
- CLAUDE.md
- agency-system/
- skills/

### Agency Knowledge
- knowledge/
- sources/
EOF

# 7. Commit e push
echo "📝 Criando commit..."
git add -A
if ! git diff --cached --quiet; then
    git commit -m "backup: $TIMESTAMP"
    COMMIT_SHA=$(git rev-parse --short HEAD)
    echo "📤 Enviando para GitHub..."
    git push origin main
    echo "✅ Backup concluído! Commit: $COMMIT_SHA"
    
    # 8. Registrar no banco (se disponível)
    if command -v psql &> /dev/null && [ -n "${DATABASE_URL:-}" ]; then
        psql "$DATABASE_URL" -c "
            INSERT INTO backup_log (backup_type, status, commit_sha, details)
            VALUES ('FULL_CONFIG', 'SUCCESS', '$COMMIT_SHA', '{\"timestamp\": \"$TIMESTAMP\", \"hostname\": \"$(hostname)\"}'::jsonb);
        " 2>/dev/null || echo "⚠️ Não foi possível registrar no banco"
    fi
else
    echo "✅ Nenhuma alteração desde o último backup"
fi

echo "🧹 Limpeza concluída"
echo "📅 Próximo backup automático: $(date -d '+1 day' '+%Y-%m-%d %H:%M' 2>/dev/null || echo 'amanhã')"
