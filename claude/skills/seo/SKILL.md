---
name: seo
description: Especialista em SEO técnico, on-page, conteúdo, arquitetura, intenção de busca, SEO local, performance e análise de oportunidades orgânicas. Use para auditorias, planejamento e otimização SEO.
---

# SEO

## FUNÇÃO

Melhorar a capacidade de um site ser compreendido, rastreado e encontrado por mecanismos de busca e, principalmente, atender à intenção do usuário.

## PRINCÍPIOS

- Intenção antes de volume.
- Utilidade antes de keyword stuffing.
- Conteúdo original e útil.
- Não inventar autoridade.
- Não prometer posições.
- Não criar conteúdo apenas para manipular ranking.

## SEO TÉCNICO

Avaliar quando aplicável:

- rastreamento;
- indexação;
- sitemap;
- robots;
- canonical;
- redirects;
- status HTTP;
- estrutura HTML;
- Core Web Vitals;
- mobile;
- dados estruturados.

## ON-PAGE

Avaliar:

- title;
- meta description;
- H1;
- headings;
- conteúdo;
- intenção;
- links internos;
- imagens;
- alt text;
- URLs.

## SEO LOCAL

Avaliar:

- Google Business Profile;
- NAP;
- páginas locais;
- avaliações;
- relevância geográfica;
- consistência das informações.

## REFERÊNCIAS

Consultar:

- references/technical-seo.md
- references/on-page.md

---

# CRAWL COMPLETO DO SITE

## OBJETIVO

Executar um crawl completo do site, classificar todas as issues por severidade, e gerar um relatório HTML acionável.

## FERRAMENTAS

- **OpenSEO MCP:** `run_site_audit`, `get_audit_issues`, `get_audit_pages`, `get_audit_status`, `list_projects`
- **Playwright:** validação rendered de páginas amostra
- **webfetch:** verificação de páginas específicas

## FLUXO DE CRAWL

### FASE 1: Crawl via OpenSEO

1. `list_projects` → obter `projectId` do domínio
2. `run_site_audit(url, maxPages=50)` → iniciar crawl
3. `get_audit_status` → monitorar progresso (aguardar conclusão)
4. `get_audit_issues` → extrair TODAS as issues分类

### FASE 2: Classificação de Issues

Classificar cada issue por:

| Severidade | Critério | Ação |
|------------|----------|------|
| CRITICAL | afeta indexação ou conversão | corrigir esta semana |
| WARNING | afeta performance ou SEO | corrigir este mês |
| INFO | melhoria oportunística | agendar |

### FASE 3: Validação Rendered (Amostra)

Selecionar até 10 páginas representativas:
- Homepage
- 3 páginas de serviço
- 1 página de contato
- 1 blog post (se existir)

Para cada uma:
- `webfetch` → extrair HTML
- Verificar: title, meta, h1, schema, noindex, canonical
- Comparar com dados do OpenSEO

### FASE 4: Análise de Links Internos

- Mapear links quebrados (`broken-internal-link`)
- Detectarredirect chains (`redirect-link`)
- Identificar páginas órfãs (`orphan-page`)
- Analisar distribuição nofollow/dofollow

### FASE 5: Validação de Schema

- Extrair todos os JSON-LD das páginas amostra
- Validar campos obrigatórios por tipo:
  - Organization: name, url (recommended: logo, contactPoint)
  - LocalBusiness: name, address (recommended: telephone, openingHours)
  - ProfessionalService: name, url (recommended: serviceType, areaServed)
  - Service: name, provider (recommended: description)
  - FAQPage: mainEntity
  - BreadcrumbList: itemListElement
- Verificar consistência com conteúdo visível
- Classificar erros por severidade

### FASE 6: Análise de Metadados

Para cada página do sitemap (ou amostra):
- Title: comprimento (50-60 chars ideal), relevância, duplicatas
- Meta description: comprimento (150-160 chars ideal), CTA, relevância
- H1: único, relevante, inclui keyword
- Canonical: presente, aponta para URL correta
- Robots: verificar noindex/nofollow indevidos

### FASE 7: Relatório HTML

Gerar relatório HTML e salvar em:
`~/Documents/SEO/{dominio}-seo-audit.html`

Criar pasta `~/Documents/SEO/` automaticamente se não existir.

## ESTRUTURA DO RELATÓRIO HTML

### Capa
- Nome do domínio
- Data da auditoria
- Agência (FVS7)

### Resumo Executivo
- Score geral (0-100)
- Total de issues por severidade
- Ação principal recomendada

### Issues por Categoria

#### Indexação
- Noindex indevido
- Robots.txt bloqueando
- Canonical conflitante
- Sitemap inconsistente

#### Links
- Links quebrados
- Redirect chains
- Páginas órfãs
- Distribuição nofollow

#### Conteúdo
- Titles ausentes/curtos/longos
- Meta descriptions ausentes/curtas/longas
- H1 ausentes/múltiplos
- Conteúdo thin

#### Performance
- Páginas lentas
- Core Web Vitals negativos
- Imagens não otimizadas

#### Schema/Dados Estruturados
- JSON-LD inválido
- Campos obrigatórios faltando
- Rich results não funcionando

### Matriz de Priorização

| Issue | Impacto | Esforço | Prioridade | Ação |
|-------|---------|---------|------------|------|
| ... | Alto/Médio/Baixo | Fácil/Médio/Difícil | P0/P1/P2 | ... |

### Ações Recomendadas

#### Quick Wins (esta semana)
1. ...
2. ...

#### Médio Prazo (este mês)
1. ...
2. ...

#### Longo Prazo (próximos 3 meses)
1. ...
2. ...

### Detalhamento por Página (Amostra)

Para cada página amostra:
- URL
- Title (comprimento, status)
- Meta description (comprimento, status)
- H1
- Schema detectado
- Issues encontradas
- Status de indexação

### Próximos Passos
- Ação 1
- Ação 2
- Ação 3

## REGRAS DE DADOS

- Usar apenas dados obtidos durante esta execução
- Nunca inventar métricas
- Identificar fonte de cada dado
- Separar dado real de estimativa
- quando não houver dado: "N/D — dado não disponível"

## OUTPUT

O relatório DEVE ser salvo em:
`~/Documents/SEO/{dominio}-seo-audit.html`

O relatório deve:
- Ser responsivo (mobile-first)
- Usar tema claro (cards brancos em fundo #f8fafc)
- Ter identidade visual profissional
- Inuir navegação interna
- Funcionar em desktop e mobile

---

# SISTEMA GLOBAL DA AGÊNCIA

Esta skill também segue as regras globais:

- `~/.claude/agency-system/SOURCE-HIERARCHY.md`
- `~/.claude/agency-system/ANTI-HALLUCINATION.md`
- `~/.claude/agency-system/WEB-RESEARCH.md`
- `~/.claude/agency-system/SKILL-ROUTER.md`
- `~/.claude/agency-system/QUALITY-CONTROL.md`

Essas regras complementam as referências específicas desta skill.
