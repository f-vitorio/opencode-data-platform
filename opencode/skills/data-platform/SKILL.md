---
name: data-platform
description: Gerencia banco de dados Supabase, backup para GitHub, sincronização markdown ↔ banco, relatórios de pipeline e keepalive. Use quando o usuário pedir para consultar/editar dados de clientes no banco, fazer backup, sincronizar, ou gerar relatórios.
---

# DATA PLATFORM — Plataforma de Dados da Agência

## 1. OBJETIVO

Gerenciar a plataforma de dados central da agência FVS7:
- Banco de dados Supabase (PostgreSQL)
- Backup automatizado para GitHub
- Sincronização entre arquivos markdown e banco
- Relatórios do pipeline comercial
- Keepalive do banco de dados

---

## 2. BANCO DE DADOS

### Configuração

Arquivo de credenciais: `~/.config/opencode/.env`

```
SUPABASE_URL=https://zhyyuiksuinwqnshklop.supabase.co
SUPABASE_ANON_KEY=sb_publishable_...
DATABASE_URL=postgresql://postgres:[SENHA]@db.zhyyuiksuinwqnshklop.supabase.co:5432/postgres
```

### Tabelas

| Tabela | Função |
|---|---|
| `clients` | Dados do cliente + pipeline (14 estágios) |
| `negotiations` | Negociações comerciais |
| `proposals` | Propostas comerciais |
| `contracts` | Contratos |
| `interactions` | Histórico de contato |
| `backup_log` | Log de backups |

### Conexão

```bash
source ~/.config/opencode/.env
psql "$DATABASE_URL" -c "SELECT * FROM clients;"
```

Sempre usar `sslmode=require` na connection string.

---

## 3. COMANDOS

### agency db status

Dashboard do pipeline.

```bash
source ~/.config/opencode/.env

echo "=== PIPELINE ==="
psql "$DATABASE_URL" -c "
SELECT stage, COUNT(*) as total 
FROM clients 
WHERE is_active = true 
GROUP BY stage 
ORDER BY CASE stage
  WHEN 'LEAD' THEN 1
  WHEN 'QUALIFICACAO' THEN 2
  WHEN 'DIAGNOSTICO' THEN 3
  WHEN 'PROPOSTA' THEN 4
  WHEN 'NEGOCIACAO' THEN 5
  WHEN 'AGUARDANDO_DECISAO' THEN 6
  WHEN 'GANHO' THEN 7
  WHEN 'CONTRATO' THEN 8
  WHEN 'ONBOARDING' THEN 9
  WHEN 'ATIVO' THEN 10
  WHEN 'EXPANSAO' THEN 11
  WHEN 'PAUSADO' THEN 12
  WHEN 'PERDIDO' THEN 13
  WHEN 'INATIVO' THEN 14
END;
"

echo "=== FOLLOW-UPS PENDENTES ==="
psql "$DATABASE_URL" -c "
SELECT company_name, contact_name, next_followup_date, next_followup_note
FROM clients 
WHERE is_active = true 
  AND next_followup_date IS NOT NULL
ORDER BY next_followup_date;
"

echo "=== NEGOCIAÇÕES ABERTAS ==="
psql "$DATABASE_URL" -c "
SELECT c.company_name, n.service_description, n.proposed_value, n.status
FROM negotiations n
JOIN clients c ON c.id = n.client_id
WHERE n.status = 'EM_ANDAMENTO';
"
```

### agency db import [arquivo.md]

Importa cliente de markdown para o banco.

```bash
source ~/.config/opencode/.env

# Extrair dados do markdown e inserir
ARQUIVO="$1"

# O agente deve:
# 1. Ler o arquivo .md
# 2. Extrair: company_name, segment, website, location, contact_name, etc.
# 3. Gerar slug a partir do nome
# 4. Verificar duplicidade: SELECT id FROM clients WHERE slug = '...'
# 5. Inserir: INSERT INTO clients (slug, company_name, ...) VALUES (...)
# 6. Inserir interação inicial: INSERT INTO interactions (client_id, interaction_type, content) VALUES (...)
```

### agency db export [client_id ou slug]

Exporta cliente do banco para markdown.

```bash
source ~/.config/opencode/.env

SLUG="$1"

# O agente deve:
# 1. Consultar: SELECT * FROM clients WHERE slug = '$SLUG'
# 2. Consultar interações: SELECT * FROM interactions WHERE client_id = X ORDER BY created_at
# 3. Consultar negociações: SELECT * FROM negotiations WHERE client_id = X
# 4. Gerar arquivo .md formatado
# 5. Salvar em ~/.config/opencode/clients/$SLUG.md
```

### agency db sync

Sincroniza markdown ↔ banco.

```bash
source ~/.config/opencode/.env

# O agente deve:
# 1. Listar arquivos em ~/.config/opencode/clients/*.md
# 2. Para cada arquivo, verificar se slug existe no banco
# 3. Se existe: comparar timestamps, atualizar o mais recente
# 4. Se não existe: importar do markdown para o banco
# 5. Verificar clientes no banco sem arquivo markdown → exportar
```

### agency backup

Backup completo para GitHub.

```bash
# O agente deve:
# 1. Sincronizar markdown ↔ banco (agency db sync)
# 2. Copiar configs: ~/.config/opencode/ (AGENTS.md, skills/, company-profile/)
# 3. Copiar knowledge: ~/.claude/AGENCY-KNOWLEDGE.md, agency-system/
# 4. cd ~/.config/opencode-backup (repo Git)
# 5. rsync configs para o repo
# 6. git add -A && git commit -m "backup: $(date)"
# 7. git push origin main
# 8. Registrar no backup_log:
#    INSERT INTO backup_log (backup_type, status, commit_sha, file_count)
#    VALUES ('FULL_CONFIG', 'SUCCESS', '<sha>', <count>)
```

### agency report [tipo]

Gera relatórios.

**pipeline:**
```sql
SELECT c.company_name, c.stage, c.opportunity_value, c.priority,
       c.next_followup_date, c.service_interest
FROM clients c
WHERE c.is_active = true
ORDER BY c.opportunity_value DESC NULLS LAST;
```

**followups:**
```sql
SELECT company_name, contact_name, next_followup_date, next_followup_note,
       CASE 
         WHEN next_followup_date < CURRENT_DATE THEN 'ATRASADO'
         WHEN next_followup_date = CURRENT_DATE THEN 'HOJE'
         ELSE 'PRÓXIMO'
       END as status
FROM clients
WHERE is_active = true AND next_followup_date IS NOT NULL
ORDER BY next_followup_date;
```

**financeiro:**
```sql
SELECT c.company_name, c.stage, c.opportunity_value, c.monthly_value,
       n.proposed_value, n.final_value
FROM clients c
LEFT JOIN negotiations n ON n.client_id = c.id
WHERE c.is_active = true;
```

**atividade:**
```sql
SELECT c.company_name, i.interaction_type, i.subject, i.created_at
FROM interactions i
JOIN clients c ON c.id = i.client_id
ORDER BY i.created_at DESC
LIMIT 20;
```

### agency keepalive

Ping no Supabase para evitar pausa (7 dias).

```bash
source ~/.config/opencode/.env
curl -s "$SUPABASE_URL/rest/v1/" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY"
```

---

## 4. REGRAS

1. **Banco é fonte de verdade** — em caso de conflito entre markdown e banco, o banco vence
2. **Nunca apagar** — usar soft delete (is_active = false)
3. **Preservar histórico** — nunca sobrescrever interactions
4. **Verificar duplicidade** — sempre checar slug antes de inserir
5. **Backup antes de mudanças grandes** — sempre rodar agency backup antes de migrações
6. **Log de operações** — registrar operações importantes no backup_log
7. **Segurança** — nunca expor DATABASE_URL em logs ou mensagens

---

## 5. INTEGRAÇÃO

### client-management
Lê e escreve na tabela `clients` e `interactions`.

### negotiation
Lê e escreve na tabela `negotiations`.

### proposals
Lê e escreve na tabela `proposals`.

### contracts
Lê e escreve na tabela `contracts`.

### pricing
Consulta `opportunity_value` e `proposed_value` para referência.
