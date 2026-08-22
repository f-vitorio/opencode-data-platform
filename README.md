# FVS7 Data Platform - Backup Repository

Backup automatizado das configuracoes do OpenCode e knowledge base da agencia FVS7 Marketing Digital.

## Conteudo

- `opencode/` — configuracoes do OpenCode (skills, agents, scripts, company-profile)
- `claude/` — knowledge base do Claude (AGENCY-KNOWLEDGE.md, agency-system/)
- `agency/` — agency knowledge base
- `BACKUP_MANIFEST.md` — manifest do ultimo backup

## Backup

Executar manualmente:
```bash
~/.config/opencode/scripts/backup-agent.sh
```

Ou agendar via cron para executar diariamente.

## Restauracao

Para restaurar um backup:
```bash
cd ~/.config/opencode-backup
rsync -av opencode/ ~/.config/opencode/
rsync -av claude/ ~/.claude/
```

## Seguranca

- NUNCA commitar arquivos .env
- NUNCA commitar chaves ou tokens
- Usar SSH para push no GitHub
# opencode-data-platform
