---
name: landing-page-audit
description: Sistema completo de auditoria comercial de sites e landing pages. Faz descoberta de todas as páginas do domínio, auditoria página por página, CRO, copywriting, UX/UI, SEO, Google Ads, GA4, Search Console, Google Business Profile, concorrentes locais, OpenSEO, oportunidades de palavras-chave, estimativa de perda de tráfego/leads e geração de relatório HTML comercial usando a skill de frontend disponível no projeto.
---

# LANDING PAGE & WEBSITE AUDIT PRO — VERSÃO PAS

## OBJETIVO

Executar uma auditoria comercial que CONVERTA.

O objetivo não é gerar um laudo técnico.

O objetivo é fazer o cliente:

1. PERCEBER que está perdendo dinheiro
2. SENTIR urgência de agir
3. ENTENDER que concorrentes estão na frente
4. VER que a solução é reconstrução em Astro com a FVS7
5. AGIR — entrar em contato

A auditoria segue o framework **PAS (Problem → Agitation → Solution)**:

- **PROBLEM:** Mostre o problema com dados
- **AGITATION:** Agite — custo de concorrência, perda diária, urgência
- **SOLUTION:** A solução é sempre reconstrução completa em Astro com a FVS7

---

## REGRA ABSOLUTA: NÃO AUDITAR APENAS A HOME

Quando receber um domínio, NÃO considerar a homepage suficiente.

A primeira obrigação é descobrir a estrutura do site.

Criar um INVENTÁRIO DE URLs.

Encontrar, quando disponíveis:

- sitemap.xml;
- sitemap index;
- robots.txt;
- links internos;
- menus;
- páginas de serviços;
- páginas de produtos;
- landing pages;
- páginas locais;
- categorias;
- artigos;
- páginas institucionais;
- contato;
- FAQ;
- páginas comerciais;
- outras páginas indexáveis.

Utilizar múltiplas fontes para descobrir URLs.

Prioridade:

1. sitemap;
2. sitemap index;
3. links internos;
4. navegação;
5. Search Console;
6. OpenSEO;
7. descoberta pelo domínio.

Se o site possuir muitas páginas, classificar e priorizar.

NUNCA assumir que a home representa todo o site.

---

## 1. INVENTÁRIO DO SITE

Antes da auditoria detalhada, produzir internamente uma tabela:

| URL | Tipo | Intenção | Importância | Status |
|---|---|---|---|---|

Classificar páginas como:

- Homepage
- Serviço
- Produto
- Landing Page
- Local
- Categoria
- Blog
- Institucional
- Contato
- Conversão
- Outro

Também identificar:

- páginas duplicadas;
- páginas muito semelhantes;
- páginas órfãs;
- páginas importantes sem links;
- páginas sem intenção clara;
- páginas sem potencial comercial.

### 1.1 DETECÇÃO DE PÁGINAS ÓRFÃS (OBRIGATÓRIO)

Páginas órfãs são URLs que existem no sitemap mas não possuem nenhum link interno apontando para elas. Um crawler que segue links nunca as descobre — só é possível detectá-las comparando o sitemap com o que foi crawleado.

**Ferramentas necessárias:**
- `webfetch` para baixar o sitemap.xml
- `get_audit_pages` do OpenSEO para ver páginas crawleadas
- `get_audit_issues` para verificar problemas de indexação

**Procedimento:**

1. Buscar o sitemap.xml do domínio (tentar `/sitemap.xml`, `/sitemap-index.xml`, ou verificar no `robots.txt`)
2. Extrair todas as URLs listadas no sitemap
3. Usar `get_audit_pages` para obter a lista de páginas que o crawl encontrou
4. Comparar: **URLs no sitemap - URLs crawleadas = páginas órfãs potenciais**
5. Para cada órfã identificada, verificar:
   - Status HTTP (200, 301, 404)
   - Tráfego orgânico (via `get_domain_keyword_suggestions` ou Search Console)
   - Número de backlinks externos (via `get_backlinks_profile`)
   - Presença no índice do Google (via `inspect_urls`)

**Output esperado:**

```
PÁGINAS ÓRFÃS DETECTADAS: X páginas

| URL | Título | Status | Tráfego | Backlinks | Ação Recomendada |
|-----|--------|--------|---------|-----------|------------------|
| /url-exemplo/ | Título | 200 | 0 | 0 | Adicionar links internos / Remover / Redirecionar |
```

**Classificação das órfãs:**
- **CRÍTICA:** Página de conversão/serviço sem links → adicionar links imediatamente
- **ALTA:** Página de conteúdo relevante sem links → adicionar links esta semana
- **MÉDIA:** Página obsoleta ou duplicada → considerar redirecionamento ou remoção
- **BAIXA:** Página irrelevante → remover do sitemap ou noindex

> **Regra:** Se o Ahrefs ou outra ferramenta externa mostrar `href inlinks = 0`, a página é confirmadamente órfã. Priorizar sempre a correção de páginas com valor comercial.

---

### 1.1.1 DETECÇÃO DE NOINDEX NO SITEMAP (OBRIGATÓRIO)

Páginas noindex no sitemap são uma contradição técnica que prejudica a indexação.

**Ferramentas necessárias:**
- `webfetch` para verificar metadados de cada página
- `get_audit_issues` do OpenSEO para verificar issues de indexação
- `inspect_urls` do OpenSEO para confirmar status de indexação

**Procedimento:**

1. Para cada URL extraída do sitemap:
   - Verificar se a página possui tag `<meta name="robots" content="noindex">`
   - Verificar se a página possui header `X-Robots-Tag: noindex`
   - Usar `get_audit_issues` com filtro `noindex-page` para identificar automaticamente

2. Se encontrar páginas noindex no sitemap:
   - Classificar: são páginas de serviço? Blog? Internas?
   - Se páginas de serviço → **CRÍTICO** (remover noindex imediatamente)
   - Se páginas internas (admin, login, thank you) → OK (remover do sitemap)

3. Output esperado:

```
PÁGINAS NOINDEX NO SITEMAP: X páginas

| URL | Tipo | Status | Ação Recomendada |
|-----|------|--------|------------------|
| /url-exemplo/ | Serviço | noindex | REMOVER noindex — página deve ser indexada |
| /admin/ | Interna | noindex | OK — remover do sitemap |
```

**Classificação de severidade:**
- **CRÍTICA:** Página de serviço/conversão com noindex → remover noindex imediatamente
- **ALTA:** Página de conteúdo com noindex → verificar se é intencional
- **MÉDIA:** Página interna com noindex no sitemap → remover do sitemap
- **BAIXA:** Página obsoleta com noindex → manter ou remover do sitemap

> **Regra:** Se o Ahrefs mostrar `noindex-page in sitemap: 10`, isso significa que 10 páginas estão no sitemap mas bloqueadas de indexação. Isso é sempre um problema, exceto para páginas que realmente não devem ser indexadas (admin, login, busca interna).

---

### 1.2 ANÁLISE DE LINKS INTERNOS (OBRIGATÓRIO)

Links internos são o sistema circulatório do site. Links quebrados, redirects e distribuição inadequada de nofollow prejudicam crawl e autoridade.

**Ferramentas necessárias:**
- `get_audit_issues` do OpenSEO (para issues de links)
- `get_audit_pages` (para mapear páginas crawleadas)
- `webfetch` (para verificar páginas específicas)

**Procedimento:**

#### 1.2.1 BROKEN LINKS

Verificar issue `broken-internal-link`:
- Mapear TODAS as ocorrências
- Para cada uma: URL origem → URL destino (404/4XX)
- Classificar por impacto (quantas páginas apontam para a quebrada)
- Recomendação: redirect 301 ou atualizar link

#### 1.2.2 REDIRECT CHAINS

Verificar issue `redirect-link`:
- Identificar cadeias de redirect (A → B → C)
- Redirecionamento máximo: 1 salto
- Recomendação: apontar direto para URL final

#### 1.2.3 PÁGINAS ÓRFÃS

Verificar issue `orphan-page`:
- Páginas sem links internos incoming
- Verificar se são páginas importantes
- Recomendação: adicionar links contextuais ou remover

#### 1.2.4 DISTRIBUIÇÃO NOFOLLOW/DOFOLLOW

Verificar:
- Links nofollow em páginas de serviço (problema — não transmite autoridade)
- Links nofollow em footer/sidebar (normal)
- Distribuição mixta nofollow/dofollow na mesma página (verificar se intencional)

**Output esperado:**

```
ANÁLISE DE LINKS INTERNOS

BROKEN LINKS: X ocorrências
| URL Origem | URL Destino | Status | Impacto | Ação |
|------------|-------------|--------|---------|------|
| /page-a/ | /page-b/ | 404 | 15 páginas afetadas | Redirect 301 |

REDIRECTS: X ocorrências
| URL Origem | URL Destino | Saltos | Ação |
|------------|-------------|--------|------|
| /old-page/ | /new-page/ | 2 | Apontar direto |

ÓRFÃS: X páginas
| URL | Tráfego | Backlinks | Ação |
|-----|---------|-----------|------|
| /content/ | 0 | 0 | Adicionar links ou remover |

NOFOLLOW: X ocorrências problemáticas
| URL | Contexto | Impacto | Ação |
|-----|----------|---------|------|
| /servico/ | Link nofollow em CTA | Não transmite autoridade | Remover nofollow |
```

**Classificação de severidade:**
- **CRÍTICA:** Links quebrados em páginas de alta autoridade → corrigir imediatamente
- **ALTA:** Muitas páginas órfãs de conteúdo relevante → adicionar links esta semana
- **MÉDIA:** Redirect chains simples → atualizar URLs diretas
- **BAIXA:** Nofollow em contextos normais (footer) → manter

---

## 2. PRIORIZAÇÃO DAS PÁGINAS

Nem todas as páginas precisam receber o mesmo nível de análise.

Priorizar:

### PRIORIDADE 1

- homepage;
- páginas de serviços;
- páginas de produtos;
- landing pages;
- páginas que recebem tráfego pago;
- páginas com maior tráfego orgânico;
- páginas com maior potencial comercial.

### PRIORIDADE 2

- páginas locais;
- categorias;
- páginas de apoio;
- páginas com potencial de SEO.

### PRIORIDADE 3

- blog;
- institucionais;
- páginas de menor impacto.

Porém:

> Páginas de baixa prioridade ainda devem ser identificadas e consideradas no diagnóstico geral.

---

## 3. DIAGNÓSTICO DE RASTREAMENTO (SEÇÃO CRÍTICA — GATILHO DE PERDA)

⚠️ **OBRIGATÓRIO:** Esta é a primeira coisa que o cliente deve ver após o inventário. É o gatilho de PERDA mais poderoso.

### 3.1. O QUE VERIFICAR

Verificar a existência de:

- **Google Analytics 4 (GA4):** tag gtag ou GTM com config GA4
- **Google Search Console (GSC):** verificação HTML ou meta tag
- **Google Tag Manager (GTM):** container GTM instalado
- **Google Ads:** tag de conversão ou ligação com GA4
- **Meta Pixel:** pixel do Facebook/Instagram
- **Conversion Tracking:** eventos de conversão configurados

### 3.2. COMO VERIFICAR

Inspecionar o HTML do site e procurar:

- `<script>` com `gtag`, `gtm`, `google_analytics`
- Meta tag `google-site-verification`
- Script do Meta Pixel
- Eventos de conversão
- DataLayer push

### 3.3. COMO APRESENTAR NO RELATÓRIO

**SE não houver rastreamento:**

```
VOCÊ ESTÁ NO ESCURO

❌ GA4 não instalado — não sabe quem visita seu site
❌ Google Search Console não verificado — não sabe para quais buscas aparece
❌ Google Tag Manager ausente — conversões não são mensuradas
❌ Sem conversion tracking — cada R$ em ads é um tiro no escuro
❌ Sem pixel de remarketing — não consegue reengajar visitantes

Enquanto isso, seus concorrentes têm todos esses dados.
Eles sabem exatamente o que funciona. Vocês estão no escuro.
```

**SE houver rastreamento parcial:**

```
RASTREAMENTO INCOMPLETO

✅ GA4 instalado — dados básicos disponíveis
❌ Google Search Console não verificado — keywords desconhecidas
❌ Google Tag Manager ausente — eventos limitados
❌ Sem conversion tracking — ROI impossível de medir
❌ Sem pixel — remarketing impossível

Você tem dados, mas não tem VISIBILIDADE COMPLETA.
```

**SE houver rastreamento completo:**

```
RASTREAMENTO FUNCIONAL

✅ GA4 instalado e configurado
✅ Google Search Console verificado
✅ Google Tag Manager ativo
✅ Conversion tracking configurado
✅ Meta Pixel ativo

Neste caso, focar em otimização e análise de dados.
```

### 3.4. CONSEQUÊNCIA FINANCEIRA

Para cada item ausente, conectar a uma consequência:

| Item Ausente | Consequência |
|---|---|
| GA4 | Você não sabe quantas pessoas visitam seu site |
| GSC | Você não sabe para quais buscas seu site aparece |
| GTM | Você não consegue rastrear eventos |
| Conversion Tracking | Você não sabe se seus anúncios funcionam |
| Meta Pixel | Você não consegue remarketing |

### 3.5. COPY PARA A SEÇÃO

> **O Problema: Você Está no Escuro**
>
> Seu site não possui rastreamento adequado. Isso significa que:
>
> - Você não sabe quantas pessoas visitam seu site por dia
> - Você não sabe de onde elas vêm
> - Você não sabe quais páginas geram mais interesse
> - Você não sabe quantas pessoas entraram em contato
> - Você não sabe se o investimento em marketing está funcionando
>
> **É como dirigir de olhos vendados.**
>
> Enquanto isso, seus concorrentes possuem dados completos sobre seu tráfego. Eles sabem exatamente quais páginas convertem, quais keywords trazem clientes, e onde investir mais.
>
> **A FVS7 resolve:** Implementação completa de GA4 + GTM + Conversion Tracking para que cada decisão seja baseada em dados reais.

---

## 4. VELOCIDADE (SEÇÃO CRÍTICA — GATILHO DE PERDA IMEDIATA)

⚠️ **OBRIGATÓRIO:** Velocidade é o gatilho mais tangível. O cliente SENTE quando um site é lento.

### 4.1. O QUE VERIFICAR

- Tempo de carregamento total
- Core Web Vitals (LCP, FID, CLS)
- Tamanho da página
- Número de requests
- Otimização de imagens
- Scripts bloqueantes
- Cache configurado

### 4.2. COMO APRESENTAR NO RELATÓRIO

```
VELOCIDADE — CADA SEGUNDO É UM CLIENTE PERDIDO

❌ Seu site demora X segundos para carregar em mobile
❌ 53% dos usuários abandonam após 3 segundos
❌ Cada segundo extra reduz conversão em 7%
❌ Google penaliza sites lentos no ranqueamento

Se 1.000 pessoas por mês tentam acessar seu site
e 53% saem por lentidão, você está perdendo 530
potenciais clientes todos os meses.
```

### 4.3. BULLET POINTS DE IMPACTO

- Site abre em X segundos — benchmark é menos de 2s
- Imagens sem otimização — carregamento pesado
- Scripts bloqueantes — conteúdo atrasado
- Hosting lento — tempo de resposta alto
- Sem cache — cada visita recarrega tudo
- Google penaliza — posicionamento cai

### 4.4. CONSEQUÊNCIA FINANCEIRA

> "Cada segundo que seu site demora para abrir, 7% dos visitantes desistem. Com 1.000 visitas/mês, isso representa 70 potenciais clientes perdidos por cada segundo de atraso."

### 4.5. POR QUE ASTRO RESOLVE

- Zero JavaScript por padrão
- Carregamento instantâneo
- 90+ no PageSpeed garantido
- Renderização no servidor

---

## 5. MOBILE (SEÇÃO CRÍTICA — GATILHO DE INUTILIDADE)

⚠️ **OBRIGATÓRIO:** Se o site não funciona no mobile, ele é INÚTIL para 70% do tráfego.

### 5.1. O QUE VERIFICAR

- Layout responsivo
- Botões com área de toque mínima (44px)
- Fonte legível (mínimo 14px)
- Imagens sem proporção
- Formulários funcionais
- Menu navegável
- Scroll horizontal
- CTA visível sem rolar

### 5.2. COMO APRESENTAR NO RELATÓRIO

```
MOBILE — SEU SITE É INÚTIL NO CELULAR?

❌ 70% das buscas por serviços são feitas no celular
❌ Layout quebrado em telas pequenas
❌ Botões pequenos demais para clicar
❌ Formulário não funciona
❌ Texto ilegível
❌ Google desconsidera versão desktop para SEO

Se 70% do seu tráfego é mobile e o site não funciona
no celular, você está desperdiçando 70% do investimento.
```

### 5.3. BULLET POINTS DE IMPACTO

- Layout quebrado em telas pequenas
- Botões menores que 44px — difícil clicar
- Fonte abaixo de 14px — difícil ler
- Imagens estourando a tela
- Formulário com teclado cobrindo campo
- Tabelas vazando para fora
- CTA abaixo da dobra — não aparece sem rolar

### 5.4. CONSEQUÊNCIA FINANCEIRA

> "Se 70% do seu tráfego é mobile e o site não funciona bem no celular, você está desperdiçando 70% do seu investimento em aquisição. É como ter uma loja com a porta trancada para a maioria dos clientes."

### 5.5. POR QUE ASTRO RESOLVE

- Design responsivo desde a concepção
- Funciona em qualquer tela
- Google usa mobile-first indexing
- Experiência nativa em dispositivos móveis

---

## 6. AUDITORIA PÁGINA POR PÁGINA

Para cada página comercial importante, avaliar de forma SIMPLIFICADA:

- URL;
- título;
- H1;
- intenção;
- proposta de valor;
- CTA;
- prova social;
- copy;
- mobile;
- velocidade.

**NÃO criar parágrafos longos de explicação técnica.**

Usar formato de BULLET POINTS:

```
PÁGINA: /servico-1

❌ Sem CTA claro
❌ Copy desalinhada com intenção de busca
❌ Sem prova social
❌ Formulário com 8 campos (muito fricção)
❌ Imagens sem otimização
❌ Não funciona bem em mobile
```

---

## 7. PÁGINAS COMERCIAIS

Para cada serviço/produto relevante, verificar SIMPLIFICADAMENTE:

- Existe página específica?
- Está indexada?
- Possui CTA?
- Possui prova?
- Pode receber tráfego Google Ads?
- Funciona em mobile?

Se um serviço importante não possui página específica:

registrar como OPORTUNIDADE ESTRUTURAL.

**Formato de apresentação:**

```
OPORTUNIDADE: Serviço [X] não possui página específica

→ Demanda existe (X buscas/mês)
→ Concorrentes já possuem página
→ Você está perdendo clientes

A FVS7 resolve: Criar landing page dedicada em Astro.
```

---

## 8. DESCOBERTA DE OPORTUNIDADES

Usar OpenSEO para pesquisar:

- palavras-chave;
- volume;
- CPC;
- intenção;
- SERP;
- concorrentes;
- domain keywords;
- oportunidades;
- gaps.

Priorizar palavras-chave:

- comerciais;
- transacionais;
- locais;
- relacionadas diretamente aos serviços;
- com potencial de geração de leads.

Não escolher keywords apenas pelo volume.

**Formato de apresentação:**

```
DEMANDA QUE EXISTE HOJE

"[keyword]" — X buscas/mês — CPC R$ Y
→ Sua página não existe
→ Concorrentes estão rankeando
→ Alguém vai capturar isso

"[keyword]" — X buscas/mês — CPC R$ Y
→ Sua página está na página 3
→ Posição atual: #25
→ Top 3: [Concorrente A], [Concorrente B], [Concorrente C]
```

---

## 9. QUANTO O CLIENTE ESTÁ PERDENDO

Sempre que houver dados suficientes, estimar oportunidades.

A análise pode considerar:

- volume de busca;
- CTR potencial;
- posição atual;
- CPC;
- tráfego atual;
- taxa de conversão;
- leads;
- custo por lead;
- valor potencial do lead.

Exemplo de raciocínio:

DEMANDA DE BUSCA
→ TRÁFEGO POTENCIAL
→ CONVERSÃO POTENCIAL
→ LEADS POTENCIAIS
→ VALOR POTENCIAL

Quando não for possível calcular com segurança:

não inventar.

Apresentar como:

"Estimativa baseada em premissas."

Mostrar as premissas utilizadas.

---

## 10. GAP DE SEO

Cruzar:

- keywords relevantes;
- volume;
- posições;
- páginas;
- concorrentes;
- intenção.

Identificar:

### GAP 1 — KEYWORD SEM PÁGINA

Existe demanda, mas o cliente não possui página adequada.

### GAP 2 — PÁGINA SEM VISIBILIDADE

Existe página, mas ela não possui boa visibilidade.

### GAP 3 — PÁGINA MAL ALINHADA

A página existe, mas não responde adequadamente à intenção.

### GAP 4 — CTR BAIXO

Existe impressão, mas poucos cliques.

### GAP 5 — CONCORRENTE À FRENTE

Concorrentes capturam demanda que o cliente poderia disputar.

**Formato de apresentação:**

```
GAP: [keyword] — X buscas/mês

❌ Você não possui página para essa busca
✅ Concorrente A possui landing page otimizada
✅ Concorrente B rankeando na posição 3

Oportunidade: Criar landing page dedicada em Astro.
```

---

## 11. GOOGLE SEARCH CONSOLE

Quando disponível, analisar:

- cliques;
- impressões;
- CTR;
- posição;
- queries;
- páginas;
- dispositivos.

Procurar:

- páginas com muitas impressões e poucos cliques;
- keywords nas posições 4–20;
- keywords comerciais com baixo CTR;
- páginas com potencial de crescimento;
- queries sem página adequada;
- páginas que estão recebendo intenção errada.

Cruzar esses dados com OpenSEO.

---

## 12. GOOGLE ADS

Quando houver Google Ads disponível:

cruzar:

KEYWORD
→ ANÚNCIO
→ LANDING PAGE
→ CONVERSÃO

Avaliar:

- relevância;
- CTR;
- CPC;
- conversões;
- CPA;
- termos de pesquisa;
- Quality Score;
- experiência da landing page.

Identificar páginas que estão sendo usadas para tráfego pago.

Verificar se existe uma página melhor para cada intenção.

**Formato de apresentação:**

```
GOOGLE ADS — TRÁFEGO SENDO DESPERDIÇADO

❌ Anúncio para "[keyword]"
   → CPC: R$ X
   → CTR: Y%
   → Conversões: 0
   → Landing page: página genérica (não otimizada)

O investimento está sendo jogado fora.
A landing page não converte.

A FVS7 resolve: Landing page dedicada em Astro + CRO.
```

---

## 13. GA4

Quando disponível, analisar:

- landing pages;
- usuários;
- sessões;
- origem;
- campanhas;
- eventos;
- conversões;
- engagement;
- dispositivos.

Procurar:

- páginas com muito tráfego e pouca conversão;
- páginas com tráfego pago e baixo resultado;
- diferenças mobile/desktop;
- páginas com comportamento anormal;
- gargalos do funil.

---

## 14. GOOGLE BUSINESS PROFILE

Quando o negócio for local ou possuir presença local, esta análise é OBRIGATÓRIA quando os dados estiverem disponíveis.

Verificar os dados do Google Business Profile.

Analisar:

- visualizações;
- pesquisas;
- ligações;
- solicitações de rota;
- cliques no site;
- ações dos usuários;
- avaliações;
- quantidade de avaliações;
- nota média;
- frequência de avaliações;
- categorias;
- categoria principal;
- categorias secundárias;
- descrição;
- serviços;
- produtos quando aplicável;
- fotos;
- frequência de atualizações;
- completude do perfil;
- consistência das informações.

Não inventar métricas.

Se o acesso ao GBP não estiver disponível:

informar:

"Dados do Google Business Profile não disponíveis para esta auditoria."

Não substituir números reais por estimativas sem deixar isso explícito.

---

## 15. GBP — ANÁLISE COMERCIAL

Não limitar a análise do GBP a "perfil completo".

Avaliar:

- potencial de geração de chamadas;
- potencial de geração de rotas;
- potencial de geração de visitas ao site;
- posicionamento local;
- categoria;
- avaliações;
- concorrentes;
- presença local.

Quando houver dados:

calcular:

- taxa de ação;
- tendência;
- crescimento;
- oportunidade.

---

## 16. CONCORRENTES LOCAIS

Para negócios locais, identificar concorrentes próximos do cliente.

Utilizar:

- OpenSEO;
- pesquisa local;
- SERP;
- Google Maps/GBP quando disponível;
- dados de mercado disponíveis.

Não comparar somente concorrentes nacionais.

Priorizar:

1. concorrentes próximos;
2. concorrentes que aparecem para as principais buscas;
3. concorrentes com forte presença local;
4. concorrentes com maior autoridade comercial.

**Formato de apresentação (PAS + gatilho de comparação):**

```
SEUS CONCORRENTES ESTÃO NA SUA FRENTE

| Critério | Você | Concorrente A | Concorrente B | Concorrente C |
|---|---|---|---|---|
| GA4 | ❌ | ✅ | ✅ | ❌ |
| GSC | ❌ | ✅ | ✅ | ✅ |
| Velocidade | Lento | Rápido | Rápido | Médio |
| Mobile | Quebrado | Perfeito | Perfeito | Funcional |
| Avaliações | [N] | 47 | 32 | 28 |
| Google Ads | Não | Sim | Não | Sim |
| Landing Pages | Genéricas | Específicas | Genéricas | Específicas |

Eles já têm o que você não tem.
Eles estão capturando os clientes que deveriam ser seus.
```

---

## 17. COPYWRITING DO RELATÓRIO — FRAMEWORK PAS

O relatório DEVE seguir o framework **PAS (Problem → Agitation → Solution)**.

### PROBLEM (PROBLEMA)

- Mostre o problema com dados reais
- Use bullet points curtos
- Não explique tecnicamente — mostre consequência

### AGITATION (AGITAÇÃO)

- Conecte cada problema a uma consequência financeira
- Compare com concorrentes
- Mostre o custo de não agir
- Use timeline de perda (30d/90d/12m)

### SOLUTION (SOLUÇÃO)

- A solução é SEMPRE reconstrução completa em Astro com a FVS7
- NUNCA Liste correções avulsas
- Destaque por que Astro é melhor
- Mostre o que o cliente recebe

**Exemplo de narrativa PAS:**

```
PROBLEMA: Seu site não tem GA4 instalado

AGITAÇÃO: Você não sabe quantas pessoas visitam seu site,
não sabe de onde vêm, não sabe o que fazem. Enquanto isso,
seus concorrentes têm dados completos e estão otimizando
cada decisão. Cada dia sem dados é uma decisão no escuro.

SOLUÇÃO: A FVS7 reconstrói seu site em Astro com rastreamento
completo (GA4 + GTM + Conversion Tracking). Você passa a ter
dados reais para tomar decisões.
```

---

## 18. RELATÓRIO VOLTADO PARA VENDA

O relatório DEVE vender reconstrução em Astro com a FVS7.

NUNCA:

- Listar correções avulsas
- Sugerir que o cliente "pode fazer sozinho"
- Passar lista de tarefas técnicas
- Depreciar o site atual sem oferecer solução completa

SEMPRE:

- Mostrar o problema
- Agitar com consequência financeira
- Comparar com concorrentes
- Oferecer reconstrução em Astro como solução
- Posicionar a FVS7 como executora

**Exemplo de copy:**

> **NÃO:** "Você deveria otimizar as imagens e corrigir o formulário."
>
> **SIM:** "Seu site atual não foi construído para converter. A FVS7 reconstrói seu site do zero em Astro — com velocidade instantânea, mobile perfeito, tracking completo e CRO integrado."

---

## 19. DADOS DA AGÊNCIA

O relatório final deve utilizar os dados institucionais da agência disponíveis no sistema.

Antes de gerar o relatório:

procurar informações em:

- agency knowledge;
- arquivos de contexto da agência;
- configuração do projeto;
- documentação institucional;
- perfil da agência;
- dados já disponíveis no ambiente.

Utilizar:

- nome da agência;
- logotipo quando disponível;
- site;
- serviços;
- posicionamento;
- diferenciais;
- informações de contato;
- identidade visual;
- CTA comercial.

NÃO inventar dados institucionais.

Se houver um arquivo oficial de identidade/branding da agência, utilizá-lo como fonte principal.

---

## 20. POSICIONAMENTO DA AGÊNCIA

O relatório deve posicionar a agência como a ÚNICA solução para os problemas encontrados.

**NUNCA:** "Existem várias opções no mercado..."

**SEMPRE:** "A FVS7 é especializada em reconstrução de sites em Astro com foco em conversão."

Relacionar problemas com serviços:

PROBLEMA:
Site lento, quebra no mobile, sem tracking, sem CRO.

SOLUÇÃO:
Reconstrução completa em Astro com a FVS7.

CAPACIDADE FVS7:
Astro + Tailwind + GTM + GA4 + CRO + SEO.

---

## 21. FRONTEND / DESIGN DO RELATÓRIO

O relatório final deve ser entregue em HTML.

NÃO entregar apenas Markdown quando o usuário solicitar auditoria completa.

O relatório DEVE ser salvo em: ~/Documents/Auditoria/{dominio}-auditoria.html

Criar a pasta ~/Documents/Auditoria/ automaticamente se não existir.

## PADRÃO VISUAL OBRIGATÓRIO

Todos os relatórios de auditoria DEVEM seguir o design padronizado.

Arquivo de referência: ~/Documents/Auditoria/auditoria-joanaozi-v2.html

Copiar EXATAMENTE o bloco `<style>` do arquivo de referência para todos os novos relatórios.

O design padrão possui:

- Tema claro (cards brancos em fundo #f8fafc)
- Capa escura com gradiente
- Fonte Inter (Google Fonts)
- Header sticky com navegação
- Section labels com uppercase
- Cards com sombra suave
- Grid responsivo (2, 3, 4 colunas)
- Barras de progresso
- Timeline com dots coloridos
- Insight boxes com gradientes
- Danger/warning boxes
- CTA section com gradiente escuro
- Footer escuro
- Data ledger script para proveniência de dados

NÃO alterar o design padrão.

NÃO criar layouts diferentes para o mesmo tipo de relatório.

Manter consistência visual entre TODOS os relatórios de auditoria.

---

## 22. DESIGN DO RELATÓRIO

O HTML deve parecer um relatório produzido por uma agência profissional.

Utilizar:

- layout responsivo;
- excelente tipografia;
- hierarquia visual;
- cards;
- tabelas;
- gráficos quando houver dados;
- indicadores;
- badges;
- barras de progresso;
- destaques;
- comparações;
- seções bem separadas;
- navegação interna;
- versão mobile;
- impressão em PDF quando possível.

Evitar:

- excesso de cores;
- aparência de dashboard genérico;
- texto sem hierarquia;
- tabelas ilegíveis;
- design infantil;
- excesso de animações.

---

## 23. ESTRUTURA VISUAL DO HTML — 13 SEÇÕES PAS

⚠️ **REGRA ABSOLUTA:** O relatório DEVE seguir a estrutura PAS com gatilhos mentais.

### LÓGICA PRINCIPAL

O cliente precisa entender IMEDIATAMENTE que está perdendo dinheiro.

A primeira coisa que ele vê depois da CAPA deve ser: "Aqui está onde seu dinheiro está sendo jogado fora."

NÃO existe "corrigir" ou "ajustar". A solução é SEMPRE reconstrução completa.

O plano NÃO é de 90 dias. É de 15 dias (reconstrução) + 30 dias (SEO + Ads).

### CAPA

- "Auditoria de Crescimento Digital"
- Pergunta de impacto: "Quanto da demanda disponível seus concorrentes estão capturando?"
- Nome do cliente, domínio, data, agência

### 01 — ONDE ESTÁ O DINHEIRO SENDO PERDIDO (PRIMEIRO IMPACTO)

⚠️ **ESTA SEÇÃO DEVE SER A PRIMEIRA APÓS A CAPA.**

O cliente deve ver IMEDIATAMENTE onde está perdendo dinheiro.

- Tabela visual com colunas: Vazamento | Evidência | Impacto
- Linhas exemplo:
  - Site não indexável | Google não vê suas páginas | ALTO — demanda invisível
  - Zero tracking | Sem GA4/GTM | CRÍTICO — decisões no escuro
  - Sem sitemap | Google não sabe o que existe | ALTO — indexação prejudicada
  - Velocidade ruim | Imagens pesadas | MÉDIO — clientes saindo
  - Mobile quebrado | Botões pequenos | MÉDIO — 70% do tráfego comprometido
  - Sem conversão | Sem formulário/CTA claro | ALTO — visitantes não viram leads
- Badge: "AQUI ESTÁ SEU DINHEIRO SENDO PERDIDO"

### 02 — VOCÊ ESTÁ PERDENDO (GATILHO: PERDA)

- Card grande: tracking ausente
- Bullet points:
  - ❌ Sem GA4 — não sabe quem visita
  - ❌ Sem GSC — não sabe para quais buscas aparece
  - ❌ Sem GTM — conversões não mensuradas
  - ❌ Sem conversion tracking — ads no escuro
  - ❌ Sem pixel — não consegue remarketing
- Badge: "VOCÊ ESTÁ NO ESCURO"

### 03 — SEUS CONCORRENTES ESTÃO NA SUA FRENTE (GATILHO: COMPARAÇÃO)

- Tabela: Cliente × concorrentes reais do mercado
- Métricas: site, indexação, tracking, SEO, avaliações, preço
- Bullet points:
  - Concorrente A: tem X páginas indexadas, você tem 1
  - Concorrente B: GA4 + GTM instalados, você tem zero
  - Concorrente C: avaliações no Google, presença local ativa
  - Concorrente D: blog com conteúdo, SEO ativo
- Badge: "ELES JÁ TÊM O QUE VOCÊ NÃO TEM"

### 04 — A DEMANDA QUE EXISTE HOJE (GATILHO: ESCASSEZ)

- Keywords com volume e CPC (quando disponível)
- Bullet points:
  - "[keyword]" — X buscas/mês — sua página não existe
  - "[keyword]" — concorrentes rankeando
  - "[keyword]" — demanda sem resposta
  - "Alguém vai capturar isso. Será você?"
- Badge: "DEMANDA DE MERCADO"

### 05 — O CUSTO DE CADA DIA QUE PASSA (GATILHO: URGÊNCIA)

- Timeline: HOJE → 15d → 30d → 90d
- Bullet points:
  - Cada dia sem dados = decisões no escuro
  - Cada dia sem velocidade = clientes saindo
  - Cada dia sem mobile = 70% do tráfego desperdiçado
  - Cada dia concorrentes fortalecem presença
  - Enquanto você espera, eles capturam sua demanda
- Badge: "O CUSTO DA INÉRCIA"

### 06 — CENÁRIO FINANCEIRO (GATILHO: VALOR)

- 3 cenários:
  - Conservador: X leads → R$ Y
  - Moderado: X leads → R$ Y
  - Agressivo: X leads → R$ Y
- Disclaimer: "Estimativa baseada em dados de mercado"
- Badge: "PROJEÇÃO FINANCEIRA"

### 07 — O SITE ATUAL (DIAGNÓSTICO RÁPIDO)

- Inventário: quantas páginas existem vs quantas deveriam existir
- Problemas críticos em bullet points (sem detalhes técnicos excessivos):
  - ❌ Site não aparece no Google
  - ❌ Nada é mensurado
  - ❌ Páginas de serviço invisíveis
  - ❌ Experiência mobile comprometida
- Badge: "DIAGNÓSTICO RÁPIDO"

### 08 — A SOLUÇÃO: RECONSTRUÇÃO COMPLETA (PAS: SOLUTION)

⚠️ **NUNCA listar correções. A solução é SEMPRE reconstrução.**

- Comparação visual: Site Atual vs Reconstrução FVS7
- Comparação:
  | Aspecto | Site Atual | Reconstrução FVS7 |
  |---|---|---|
  | Tecnologia | SPA React (não indexável) | Astro SSG (indexável) |
  | Páginas | 1 (home) | Múltiplas (serviço, blog, FAQ) |
  | Tracking | Nenhum | GA4 + GTM completo |
  | Velocidade | 1.1MB hero | <200KB otimizado |
  | Mobile | Touch targets quebrados | Mobile-first perfeito |
  | SEO | Invisível | Técnico impecável |
  | Conversão | Sem formulário | CRO integrado |
- O que você recebe:
  - Site reconstruído do zero em Astro
  - Páginas por cada serviço/especialidade
  - Tracking completo (GA4 + GTM + conversões)
  - SEO técnico impecável
  - Mobile perfeito
  - CRO integrado
  - Formulário de captação
- Badge: "RECONSTRUÇÃO COMPLETA — NÃO CORREÇÃO"

### 09 — POR QUE FVS7 (CREDIBILIDADE)

- 5 capacidades conectadas a problemas:
  - Performance (Astro + Tailwind) → site rápido
  - Mobile-first → 70% do tráfego funciona
  - CRO → visitantes viram clientes
  - Tracking (GTM + GA4) → dados para decidir
  - SEO + Ads → demanda capturada
- Badge: "A GENTE SABE RESOLVER ISSO"

### 10 — PLANO: 15 DIAS + 30 DIAS (AÇÃO IMEDIATA)

⚠️ **O plano NÃO é de 90 dias. É de reconstrução imediata.**

- Timeline visual:
  - **Semana 1-2 (15 dias): RECONSTRUÇÃO COMPLETA**
    - Site novo em Astro
    - Todas as páginas de serviço
    - Tracking completo (GA4 + GTM)
    - SEO técnico (sitemap, canonical, schema)
    - Mobile perfeito
    - Formulário de captação
  - **Semana 3-4 (30 dias): ATIVAÇÃO**
    - SEO on-page + conteúdo
    - Google Business Profile
    - Primeiras campanhas Google Ads
    - Landing pages por campanha
    - Conversão de leads
  - **Mês 2+: OTIMIZAÇÃO CONTÍNUA**
    - Análise de dados
    - Otimização de conversão
    - Escala de Ads
    - Conteúdo blog
- Badge: "RECONSTRUÇÃO EM 15 DIAS — ATIVAÇÃO EM 30 DIAS"

### 11 — PRÓXIMO PASSO (CTA)

- "Você já viu o problema. Cada dia que passa é dinheiro sendo perdido."
- Contatos da FVS7:
  - WhatsApp: [número]
  - Email: [email]
  - Site: [URL]
- Capacidades: SEO + Google Ads + CRO + Tracking + Performance
- Badge: "AGENDE UMA CONVERSA AGORA"

---

## 24. RELATÓRIO POR PÁGINA

Para páginas comerciais prioritárias, apresentar de forma SIMPLIFICADA:

### URL

### PROBLEMAS (bullet points)
- ❌ Problema 1
- ❌ Problema 2
- ❌ Problema 3

### CONSEQUÊNCIA
Uma frase conectando problema a perda financeira.

### SOLUÇÃO
"A FVS7 reconstrói essa página em Astro com CRO integrado."

---

## 25. SCORE

Usar escala de 0–100 para visão executiva.

Categorias:

- Conversão;
- SEO;
- Google Ads;
- UX;
- Copy;
- Performance;
- Mobile;
- Confiança;
- Presença Local;
- Tracking.

O score é diagnóstico.

Não apresentar como métrica oficial do Google.

---

## 26. IMPACTO FINANCEIRO

Sempre que possível, quantificar:

- tráfego perdido;
- demanda não capturada;
- leads potenciais;
- custo de oportunidade;
- oportunidades de conversão.

Sempre apresentar:

### DADO REAL

ou

### ESTIMATIVA

ou

### HIPÓTESE

Nunca misturar.

---

## 27. MATRIZ DE PRIORIDADE

Para cada recomendação:

IMPACTO:
- Muito alto
- Alto
- Médio
- Baixo

ESFORÇO:
- Muito baixo
- Baixo
- Médio
- Alto

PRIORIDADE:

P0 — Crítico
P1 — Alto
P2 — Médio
P3 — Baixo

Priorizar:

ALTO IMPACTO + BAIXO ESFORÇO

---

## 28. 80/20

Encontrar:

### TOP 5 PROBLEMAS

que mais prejudicam o resultado.

### TOP 5 OPORTUNIDADES

com maior potencial de crescimento.

### TOP 10 AÇÕES

que devem ser executadas primeiro.

Não transformar o relatório em uma lista infinita.

---

## 29. COPY DA RECOMENDAÇÃO — FORMATO PAS

Cada recomendação DEVE seguir o formato PAS:

```
PROBLEMA: [descrição curta]

CONSEQUÊNCIA: [perda financeira em 1 frase]

SOLUÇÃO: Reconstrução em Astro com a FVS7.
```

**NUNCA:**

```
PROBLEMA: [descrição]

RECOMENDAÇÃO: Corrigir X, otimizar Y, melhorar Z.
```

**SEMPRE:**

```
PROBLEMA: [descrição]

CONSEQUÊNCIA: [perda financeira]

SOLUÇÃO: A FVS7 reconstrói seu site em Astro com [benefício].
```

---

## 30. TESTES E HIPÓTESES

Quando não houver certeza:

criar hipótese.

Para cada hipótese:

- hipótese;
- motivo;
- mudança;
- métrica;
- critério de sucesso.

Não apresentar hipótese como conclusão definitiva.

---

## 31. REGRAS DE DADOS

Nunca inventar:

- métricas;
- tráfego;
- leads;
- conversões;
- avaliações;
- posição;
- volume;
- CPC;
- concorrentes;
- GBP;
- performance;
- resultados financeiros.

Quando não houver dados:

"N/D — dado não disponível."

Quando houver estimativa:

"Estimativa."

Sempre explicar premissas relevantes.

---

## 32. PROFUNDIDADE MÍNIMA

Uma auditoria completa deve obrigatoriamente conter:

1. inventário do site;
2. **diagnóstico de rastreamento (GA4/GSC/GTM/Ads)**;
3. **análise de velocidade**;
4. **análise de mobile**;
5. análise das páginas comerciais;
6. análise da home;
7. análise das páginas de serviço;
8. SEO;
9. OpenSEO;
10. Google Ads quando disponível;
11. GA4 quando disponível;
12. Search Console quando disponível;
13. GBP quando aplicável;
14. concorrentes locais;
15. CRO;
16. copywriting;
17. UX;
18. **tracking**;
19. **velocidade**;
20. **mobile**;
21. oportunidades;
22. estimativa de perda/oportunidade;
23. **solução: reconstrução em Astro**;
24. plano de ação;
25. relatório HTML.

Se qualquer uma dessas áreas não puder ser analisada:

informar explicitamente o motivo.

---

## 33. FLUXO OBRIGATÓRIO

Executar nesta ordem:

FASE 1
→ Descobrir domínio e estrutura.

FASE 2
→ Criar inventário de URLs.

FASE 3
→ **Verificar rastreamento (GA4/GSC/GTM/Ads/Pixel).**

FASE 4
→ **Verificar velocidade.**

FASE 5
→ **Verificar mobile.**

FASE 6
→ Identificar páginas comerciais.

FASE 7
→ Auditar páginas prioritárias.

FASE 8
→ Consultar OpenSEO.

FASE 9
→ Consultar Search Console.

FASE 10
→ Consultar GA4.

FASE 11
→ Consultar Google Ads.

FASE 12
→ Consultar dados GBP quando disponíveis.

FASE 13
→ Identificar concorrentes locais.

FASE 14
→ Comparar cliente × concorrentes.

FASE 15
→ Calcular oportunidades e perdas estimadas.

FASE 16
→ Aplicar análise 80/20.

FASE 17
→ **Construir narrativa PAS (Problem → Agitation → Solution).**

FASE 18
→ Construir relatório HTML.

FASE 19
→ Revisar o relatório antes de entregar.

FASE 20
→ Salvar o relatório HTML em ~/Documents/Auditoria/{dominio}-auditoria.html
→ Criar a pasta ~/Documents/Auditoria/ se não existir
→ Nome do arquivo: {dominio}-auditoria.html (ex: mpo24h-auditoria.html)

FASE 21
→ Salvar lead no banco Supabase (tabela clients)
→ Salvar auditoria como interaction (tipo AUDITORIA)
→ Verificar se lead já existe (por slug/domínio)
→ Atualizar dados se já existir
→ Seguir protocolo da seção "FLUXO PÓS-AUDITORIA — BANCO DE DADOS"

FASE 22
→ Gerar pitch de vendas para WhatsApp em TXT
→ Salvar em ~/Documents/Auditoria/{dominio}-pitch.txt
→ Usar template fixo da seção "36. PITCH DE VENDAS PARA WHATSAPP"
→ Extrair dados do DATA_LEDGER (score, problemas, perdas financeiras)
→ Seção Google Ads é CONDICIONAL — só incluir se cliente tiver Google Ads ativo
→ Usar emojis nos problemas (⚠️) e nas perdas (💸📉🚨💰)
→ NUNCA mencionar preço no pitch
→ Seguir template fielmente — não inventar estrutura

---

## 33.1. FLUXO PÓS-AUDITORIA — BANCO DE DADOS

⚠️ **OBRIGATÓRIO:** Toda auditoria executada por esta skill DEVE resultar no salvamento do lead no banco Supabase. Sem exceções.

### 33.1.1. CONEXÃO

Usar credenciais de `~/.config/opencode/.env`:

```
SUPABASE_URL
SUPABASE_ANON_KEY
```

Conexão via API REST do Supabase (não usar psql — pode não estar instalado).

### 33.1.2. VERIFICAR SE LEAD JÁ EXISTE

```bash
source ~/.config/opencode/.env
curl -s "$SUPABASE_URL/rest/v1/clients?select=id,slug&slug=eq.{DOMINIO}" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY"
```

Se retornar resultado → UPDATE. Se vazio → INSERT.

### 33.1.3. DADOS OBRIGATÓRIOS NO CLIENTS

| Campo | Valor |
|---|---|
| slug | Domínio sem pontuação (ex: `cazzagiare`) |
| company_name | Nome da empresa extraído do site |
| segment | Segmento de atuação |
| website | URL completa do site |
| location | Cidade/Estado |
| contact_name | Nome do contato (se disponível) |
| contact_phone | Telefone/WhatsApp (se disponível) |
| contact_email | Email (se disponível) |
| stage | `DIAGNOSTICO` |
| origin | `Auditoria FVS7` |
| service_interest | Serviços identificados na auditoria |
| priority | `CRITICAL` (score <30) / `HIGH` (30-50) / `MEDIA` (50-70) / `BAIXA` (>70) |
| opportunity_value | Valor estimado de oportunidade (se disponível) |
| notes | Resumo completo da auditoria |
| agency_services | Serviços FVS7 necessários (array) |

### 33.1.4. DADOS OBRIGATÓRIOS NA INTERACTION

| Campo | Valor |
|---|---|
| client_id | ID do cliente inserido/atualizado |
| interaction_type | `AUDITORIA` |
| subject | `Auditoria Completa — {domínio}` |
| content | Resumo: score, problemas top 5, oportunidades top 5, dados do negócio |
| context | Data da auditoria, ferramenta utilizada |
| requires_followup | `true` |
| followup_date | 7 dias após a data da auditoria |
| followup_note | `Apresentar resultados da auditoria e propor reconstrução em Astro` |

### 33.1.5. PAYLOAD PADRÃO — INSERT CLIENT

```json
{
  "slug": "{DOMINIO_SE_PONTUACAO}",
  "company_name": "{NOME}",
  "segment": "{SEGMENTO}",
  "website": "{URL_COMPLETA}",
  "location": "{CIDADE}, {ESTADO}",
  "contact_name": null,
  "contact_phone": null,
  "contact_email": null,
  "stage": "DIAGNOSTICO",
  "origin": "Auditoria FVS7",
  "service_interest": "{SERVICOS_IDENTIFICADOS}",
  "priority": "{CRITICAL|HIGH|MEDIA}",
  "opportunity_value": null,
  "monthly_value": null,
  "estimated_value": null,
  "is_active": true,
  "is_client": false,
  "first_contact_date": "{DATA_ATUAL}",
  "notes": "{RESUMO_AUDITORIA}"
}
```

### 33.1.6. PAYLOAD PADRÃO — INSERT INTERACTION

```json
{
  "client_id": {ID_CLIENT},
  "interaction_type": "AUDITORIA",
  "subject": "Auditoria Completa — {DOMINIO}",
  "content": "SCORE: {X}/100\n\nPROBLEMAS:\n1. ...\n2. ...\n\nOPORTUNIDADES:\n1. ...\n2. ...\n\nSOLUÇÃO: Reconstrução em Astro com a FVS7\n\nRELATORIO: ~/Documents/Auditoria/{dominio}-auditoria.html",
  "context": "Auditoria realizada em {DATA} via landing-page-audit skill.",
  "requires_followup": true,
  "followup_date": "{DATA + 7 DIAS}",
  "followup_note": "Apresentar resultados da auditoria e propor reconstrução em Astro"
}
```

### 33.1.7. COMANDO DE INSERÇÃO (EXEMPLO)

```bash
source ~/.config/opencode/.env

# Inserir cliente
curl -s -X POST "$SUPABASE_URL/rest/v1/clients" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d '{"slug":"exemplo","company_name":"Exemplo LTDA","stage":"DIAGNOSTICO","origin":"Auditoria FVS7","is_active":true}'

# Inserir interação
curl -s -X POST "$SUPABASE_URL/rest/v1/interactions" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d '{"client_id":{ID},"interaction_type":"AUDITORIA","subject":"Auditoria Completa — exemplo","content":"..."}'
```

### 33.1.8. ERROS COMUNS

| Erro | Causa | Solução |
|---|---|---|
| `23505` duplicate key | Slug já existe | Usar UPDATE em vez de INSERT |
| `PGRST102` invalid json | Aspas ou caracteres especiais | Escapar strings corretamente |
| `401` unauthorized | API key inválida | Verificar SUPABASE_ANON_KEY no .env |

---

## 34. QA DO RELATÓRIO

Antes de finalizar:

### CHECKLIST OBRIGATÓRIAS — 13 SEÇÕES PAS

⚠️ **Se qualquer seção estiver faltando, o relatório NÃO deve ser entregue.**

- [ ] CAPA — nome, domínio, data, agência, pergunta de impacto
- [ ] 01 — Onde Está o Dinheiro (PRIMEIRA seção após capa — tabela de vazamentos)
- [ ] 02 — Você Está Perdendo (tracking ausente — gatilho PERDA)
- [ ] 03 — Concorrentes à Frente (comparação — gatilho COMPARAÇÃO)
- [ ] 04 — Demanda que Existe (keywords — gatilho ESCASSEZ)
- [ ] 05 — Custo de Cada Dia (timeline — gatilho URGÊNCIA)
- [ ] 06 — Cenário Financeiro (3 cenários + disclaimer — gatilho VALOR)
- [ ] 07 — O Site Atual (diagnóstico rápido)
- [ ] 08 — A Solução: Reconstrução Completa (NUNCA lista de correções — SEMPRE reconstrução em Astro)
- [ ] 09 — Por Que FVS7 (5 capacidades × problemas)
- [ ] 10 — Plano 15+30 Dias (reconstrução em 15 dias, ativação em 30 dias)
- [ ] 11 — Próximo Passo (CTA da FVS7)

### CHECKLIST DE GATILHOS MENTAIS

- [ ] **Onde está o dinheiro** é a PRIMEIRA seção após a capa
- [ ] **Perda** aparece nas seções 02, 05
- [ ] **Comparação** aparece na seção 03
- [ ] **Escassez** aparece na seção 04
- [ ] **Urgência** aparece na seção 05
- [ ] **Valor** aparece na seção 06
- [ ] **Solução é SEMPRE reconstrução completa** — NUNCA "correção" ou "ajuste"
- [ ] **Plano é de 15+30 dias** — NUNCA 90 dias

### CHECKLIST TÉCNICO

- todas as páginas importantes foram analisadas?
- a home não foi tratada como o site inteiro?
- as páginas de serviço foram avaliadas?
- as principais keywords foram analisadas?
- OpenSEO foi utilizado quando disponível?
- GBP foi analisado quando aplicável?
- concorrentes próximos foram analisados?
- dados reais estão diferenciados de estimativas?
- os números fazem sentido?
- disclaimer está presente na seção 06?
- o relatório possui dados da agência?
- o branding da agência foi aplicado?
- o relatório está visualmente profissional?
- o HTML funciona em desktop?
- o HTML funciona em mobile?
- o CTA da agência está presente (WhatsApp FVS7)?
- **NENHUMA lista de correções aparece no relatório?**
- **A solução é SEMPRE reconstrução completa em Astro?**
- **"Onde Está o Dinheiro" é a primeira seção após a capa?**
- **O plano é de 15+30 dias (não 90)?**
- lead foi salvo no banco Supabase?
- interação de auditoria foi registrada?
- pitch de vendas TXT foi gerado em ~/Documents/Auditoria/{dominio}-pitch.txt?
- pitch usa nome da empresa (não pessoa)?
- pitch não menciona preço?
- pitch contém dados reais do DATA_LEDGER?
- pitch tem seção Google Ads condicional (só se aplicável)?
- pitch tem emojis nos problemas e perdas?
- pitch tem impacto financeiro (mensal + anual)?
- pitch tem CTA no final?

Se a resposta for NÃO para algum item relevante:

corrigir antes de entregar.

---

## 35. REGRA FINAL

O objetivo desta Skill é produzir uma auditoria que o cliente leia e pense:

> "Agora eu entendi exatamente onde estou perdendo dinheiro."

E depois:

> "Preciso reconstruir meu site AGORA com a FVS7."

O relatório deve transformar:

DADOS
→ ONDE ESTÁ O DINHEIRO SENDO PERDIDO (primeira seção)
→ PROBLEMA
→ AGITAÇÃO (custo de não agir + comparação com concorrentes)
→ SOLUÇÃO (reconstrução completa em Astro — NUNCA correção)
→ AÇÃO IMEDIATA (plano de 15+30 dias)

A auditoria deve ser comercialmente persuasiva, visualmente profissional e baseada em evidências.

NUNCA:

- Listar correções avulsas
- Sugerir que o cliente pode fazer sozinho
- Depreciar sem oferecer solução completa
- Apresentar plano de 90 dias (o plano é de 15+30)

SEMPRE:

- Mostrar o problema
- Agitar com consequência financeira
- Comparar com concorrentes
- Oferecer reconstrução em Astro
- Posicionar a FVS7 como executora

---

## 36. PITCH DE VENDAS PARA WHATSAPP

Após gerar o relatório HTML e salvar no Supabase, gerar um **arquivo TXT** com o pitch de vendas para o vendedor enviar ao cliente via WhatsApp.

### 36.1. FUNÇÃO

Gerar um pitch curto, direto e persuasivo que:
- Descreva os erros encontrados na auditoria
- Mostre o impacto financeiro (quanto o cliente está perdendo)
- Ofereça uma auditoria da conta Google Ads (se aplicável)
- Use gatilhos mentais para gerar urgência
- NUNCA mencione preço

### 36.2. LOCAL DE SALVAMENTO

```
~/Documents/Auditoria/{dominio}-pitch.txt
```

Exemplo: `~/Documents/Auditoria/cepapsicologia-pitch.txt`

### 36.3. TEMPLATE FIXO

O pitch DEVE seguir este template fielmente. O conteúdo muda, mas a estrutura é fixa:

```
Boa tarde, [EMPRESA]!

Fiz uma auditoria gratuita do [DOMINIO] e preciso te mostrar algo urgente.

[EMPRESA] tem [ANOS] anos, [UNIDADES] unidades e [ESPECIALIDADES] especialidades — mas o site não converte. E o Google Ads está pagando por isso.

🔴 O que encontrei no site:

• ⚠️ [PROBLEMA_1]
• ⚠️ [PROBLEMA_2]
• ⚠️ [PROBLEMA_3]
• ⚠️ [PROBLEMA_4]
• ⚠️ [PROBLEMA_5]

[SE GOOGLE ADS APLICÁVEL]:
🔴 O que encontrei no Google Ads:

• 💸 [PROBLEMA_ADS_1]
• 💸 [PROBLEMA_ADS_2]
• 💸 [PROBLEMA_ADS_3]

💰 O impacto real:

• 📉 +[VOLUME] buscas/mês sem captura
• 💸 R$ [PERDA_MENSAL]/mês em leads perdidos
• 🚨 R$ [PERDA_ANUAL]/ano saindo do bolso
[SE GOOGLE ADS APLICÁVEL]:
• ⚠️ Orçamento de Google Ads sendo desperdiçado

Anexo o relatório completo com todos os dados.

[SE GOOGLE ADS APLICÁVEL]:
Quer que eu faça uma auditoria da conta de Google Ads e te prove quanto está sendo desperdiçado?

[SE SEM GOOGLE ADS]:
Quer que eu faça uma auditoria completa e te prove quanto está sendo perdido?

Abraço,
[FULANO]
FVS7 Marketing Digital
```

### 36.4. REGRAS DE PREENCHIMENTO

| Campo | Fonte | Regra |
|---|---|---|
| [EMPRESA] | Nome da empresa extraído do site | Usar nome da empresa, NUNCA nome de pessoa |
| [DOMINIO] | Domínio do site | Incluir .com ou .com.br |
| [ANOS] | Dado real do site ou estimativa explícita | Se não encontrar, usar "décadas de" |
| [UNIDADES] | Dado real do site | Se não encontrar, omitir a linha |
| [ESPECIALIDADES] | Dado real do site | Contar serviços distintos |
| [PROBLEMAS_SITE] | Problemas reais da auditoria | Usar dados do DATA_LEDGER |
| [PROBLEMAS_ADS] | Problemas reais do Google Ads | Só incluir se cliente tiver Google Ads |
| [VOLUME] | Dados de keyword research | Usar dados do OpenSEO ou estimativa |
| [PERDA_MENSAL] | Cálculo da seção 09 | Usar dados do DATA_LEDGER |
| [PERDA_ANUAL] | PERDA_MENSAL × 12 | Usar dados do DATA_LEDGER |

### 36.5. GATILHOS MENTAIS OBRIGATÓRIOS

| Gatilho | Onde aparece | Emoji |
|---|---|---|
| **Aversão à perda** | Impacto financeiro (perda mensal/anual) | 💸📉🚨 |
| **Autoridade** | "Auditoria técnica com dados" | — |
| **Urgência** | "Algo urgente" + perda mensal recorrente | — |
| **Escassez** | Concorrentes capturando demanda | ⚠️ |
| **Prova** | Dados reais do DATA_LEDGER | — |
| **Reciprocidade** | "Auditoria gratuita" + relatório anexo | — |

### 36.6. EMOJIS — ONDE APLICAR

| Elemento | Emoji | Uso |
|---|---|---|
| Título da seção "site" | 🔴 | Chamar atenção |
| Cada problema do site | ⚠️ | Alertar |
| Título da seção "Google Ads" | 🔴 | Chamar atenção |
| Cada problema do Google Ads | 💸 | Dinheiro desperdiçado |
| Título "impacto real" | 💰 | Finanças |
| Buscas sem captura | 📉 | Oportunidade perdida |
| Perda mensal | 💸 | Dinheiro saindo |
| Perda anual | 🚨 | Urgência |
| Orçamento desperdiçado | ⚠️ | Alerta |

### 36.7. CONDICIONALIDADE — GOOGLE ADS

| Seção | Incluir se... |
|---|---|
| "O que encontrei no Google Ads" | Cliente tiver Google Ads ativo |
| "Orçamento sendo desperdiçado" | Cliente tiver Google Ads ativo |
| CTA "auditoria da conta Google Ads" | Cliente tiver Google Ads ativo |
| CTA alternativo (sem Ads) | Cliente NÃO tiver Google Ads |
| Seção de impacto financeiro | SEMPRE incluir |

### 36.8. O QUE NUNCA FAZER

- NUNCA mencionar preço no pitch
- NUNCA inventar dados — usar apenas dados do DATA_LEDGER
- NUNCA usar nome de pessoa — sempre nome da empresa
- NUNCA pular a seção de impacto financeiro
- NUNCA incluir Google Ads se o cliente não tiver
- NUNCA mudar a estrutura do template

### 36.9. CHECKLIST DE VALIDAÇÃO DO PITCH

Antes de salvar o TXT:

- [ ] Usa nome da empresa (não pessoa)
- [ ] Dados reais do DATA_LEDGER (não inventados)
- [ ] Não menciona preço
- [ ] Seção Google Ads condicional (só se aplicável)
- [ ] Emojis nos problemas (⚠️) e perdas (💸📉🚨)
- [ ] Impacto financeiro presente (mensal + anual)
- [ ] CTA claro no final
- [ ] Template fiel à estrutura 36.3

---

# ============================================================
# PROTOCOLO CRÍTICO — INTEGRIDADE ABSOLUTA DOS DADOS
# ============================================================

## REGRA ZERO

ESTA REGRA TEM PRIORIDADE SOBRE TODO O RESTANTE DESTA SKILL.

NUNCA INVENTAR, COMPLETAR, ARREDONDAR, ESTIMAR OU INFERIR UM DADO E APRESENTÁ-LO COMO DADO REAL.

Isso inclui absolutamente qualquer:

- número;
- percentual;
- quantidade;
- avaliação;
- nota;
- métrica;
- posição;
- volume;
- preço;
- tráfego;
- conversão;
- custo;
- CPC;
- CTR;
- CPA;
- ROAS;
- Core Web Vital;
- PageSpeed;
- métrica do GBP;
- métrica do GA4;
- métrica do Search Console;
- keyword volume;
- dado de concorrente.

Se o valor NÃO foi obtido diretamente de uma fonte consultada DURANTE ESTA AUDITORIA:

NÃO COLOCAR O VALOR NO RELATÓRIO.

---

# 1. PROTOCOLO DE PROVENIÊNCIA

Todo dado quantitativo usado no relatório deve possuir uma origem conhecida.

Exemplos:

GBP
→ Google Business Profile / ferramenta conectada

SEO
→ OpenSEO / Search Console

Google Ads
→ Google Ads MCP

Analytics
→ GA4

Performance
→ ferramenta de performance realmente executada

Site
→ inspeção direta da URL

Concorrentes
→ fonte efetivamente consultada

Se a ferramenta retornar um valor:

usar exatamente o valor retornado.

NÃO modificar.

NÃO arredondar.

NÃO substituir.

NÃO "corrigir" baseado em outra fonte.

---

# 2. PROIBIÇÃO DE MEMÓRIA

NÃO utilizar:

- dados de auditorias anteriores;
- dados de conversas anteriores;
- números encontrados anteriormente;
- números presentes em prompts antigos;
- valores estimados em outra análise;
- valores que "parecem corretos";
- conhecimento prévio sobre o cliente.

A auditoria deve utilizar somente os dados disponíveis e verificados na execução atual.

---

# 3. PROIBIÇÃO DE PREENCHIMENTO

Se uma ferramenta não retornar determinado dado:

usar:

"N/D — dado não disponível nesta auditoria."

NUNCA preencher com:

- aproximação;
- estimativa silenciosa;
- média;
- valor anterior;
- valor presumido;
- valor encontrado em outra página;
- valor encontrado em snippet sem confirmação;
- valor inventado.

---

# 4. GBP — REGRA ESPECIAL

Os dados do Google Business Profile possuem alto risco comercial.

Portanto:

SE houver acesso aos dados do GBP:

mostrar os números retornados pela fonte.

SE não houver acesso:

informar claramente:

"Os dados internos do Google Business Profile não estavam disponíveis nesta auditoria."

NÃO estimar.

NÃO inferir.

NÃO contar avaliações visualmente de uma página e tratar isso como métrica oficial se a fonte não permitir confirmação.

NÃO utilizar número de avaliações encontrado anteriormente.

NÃO utilizar número aproximado.

Exemplo:

CORRETO:

"35 avaliações — fonte: consulta realizada durante esta auditoria."

INCORRETO:

"29 avaliações."

quando a fonte atual não retornou 29.

---

# 5. VALIDAÇÃO FINAL DOS NÚMEROS

Antes de gerar o HTML, executar uma revisão específica:

## DATA VALIDATION CHECK

Para cada número existente no relatório:

1. Qual é a fonte?
2. A fonte foi consultada nesta execução?
3. O número veio diretamente da fonte?
4. O número foi alterado?
5. O número foi arredondado?
6. O número foi inferido?
7. O número foi copiado de uma análise anterior?

Se qualquer resposta gerar dúvida:

REMOVER O NÚMERO.

Substituir por:

"N/D — dado não disponível."

---

# 6. ESTIMATIVAS FINANCEIRAS

Estimativas são permitidas SOMENTE quando claramente identificadas.

Nunca apresentar:

"Você está perdendo R$ 10.000."

sem dados suficientes.

Usar:

"Estimativa de oportunidade"

e apresentar:

- dados utilizados;
- premissas;
- fórmula;
- intervalo quando apropriado;
- nível de confiança.

Exemplo:

"Com base em X buscas mensais, CTR hipotético de Y% e taxa de conversão de Z%, a oportunidade estimada seria de aproximadamente N leads/mês. Trata-se de uma projeção, não de um dado observado."

---

# 7. SEPARAÇÃO OBRIGATÓRIA

O relatório deve diferenciar visualmente:

DADO REAL

OBSERVADO

INFERÊNCIA

ESTIMATIVA

HIPÓTESE

Nunca misturar essas categorias.

---

# ============================================================
# DATA_LEDGER — SISTEMA DE PROVENIÊNCIA DE DADOS
# ============================================================

# 8. OBJETIVO DO DATA_LEDGER

Todo relatório deve gerar internamente um DATA_LEDGER — um registro estruturado de TODOS os dados utilizados, com rastreabilidade completa.

O DATA_LEDGER é o mecanismo que garante:

- integridade dos números;
- transparência com o cliente;
- capacidade de verificação;
- separação entre dado real e estimativa.

---

# 9. ESTRUTURA DO DATA_LEDGER

Cada entrada do DATA_LEDGER deve conter:

```
{
  "id": "R01" ou "E01",
  "metric": "nome_da_metrica",
  "value": "valor ou faixa",
  "source": "fonte consultada",
  "date": "YYYY-MM-DD",
  "type": "real | estimativa | projecao",
  "context": "contexto da medição"
}
```

### CONVENÇÃO DE IDs

- **R01–R99:** Dados reais (coletados diretamente durante esta auditoria)
- **E01–E99:** Estimativas de mercado (fontes externas validadas)
- **P01–P99:** Projeções financeiras (resultados de cálculos com premissas explícitas)

---

# 10. REGRAS DO DATA_LEDGER

## 10.1. TIPO: REAL

Um dado é classificado como "real" SOMENTE quando:

- foi coletado diretamente durante esta auditoria;
- a fonte foi consultada em tempo real;
- o valor veio diretamente da ferramenta/inspeção;
- não foi modificado, arredondado ou inferido.

Exemplos de dados reais:

- CLS medido via Playwright PerformanceObserver
- número de avaliações obtido via consulta ao Google
- robots.txt inspecionado diretamente
- schema verificado via HTML
- tracking verificado via inspeção de tags
- **GA4 detectado/não detectado via inspeção**
- **GSC verificado/não verificado via inspeção**
- **GTM instalado/não instalado via inspeção**

## 10.2. TIPO: ESTIMATIVA

Um dado é classificado como "estimativa" quando:

- não foi coletado diretamente nesta auditoria;
- foi obtido de fonte de mercado ou benchmark;
- representa uma faixa, não um valor exato.

Toda estimativa DEVE:

- identificar a fonte;
- mostrar a faixa completa;
- explicitar que é estimativa;
- NUNCA ser misturada com dados reais no mesmo card/tabela sem separação visual.

## 10.3. TIPO: PROJEÇÃO

Um dado é classificado como "projeção" quando:

- é resultado de um cálculo baseado em dados reais + estimativas + premissas;
- representa um cenário, não um fato observado.

Toda projeção DEVE:

- explicitar TODAS as premissas utilizadas;
- mostrar a fórmula de cálculo;
- apresentar cenários (conservador/moderado/agressivo) quando aplicável;
- conter disclaimer visível;
- NUNCA ser apresentada como garantia de resultado.

---

# 11. EMBUTIR DATA_LEDGER NO HTML

O DATA_LEDGER deve ser embutido no HTML do relatório como JSON:

```html
<script id="data-ledger" type="application/json">
{
  "metadata": {
    "client": "Nome do Cliente",
    "domain": "dominio.com.br",
    "audit_date": "YYYY-MM-DD",
    "auditor": "FVS7 Marketing Digital",
    "version": "4.0"
  },
  "ledger": [
    {"id": "R01", "metric": "...", "value": "...", "source": "...", "date": "...", "type": "real", "context": "..."},
    {"id": "E01", "metric": "...", "value_range": "...", "source": "...", "date": "...", "type": "estimativa", "context": "..."}
  ]
}
</script>
```

Isso permite que:

- o cliente verifique a origem de qualquer número;
- a agência mantenha rastreabilidade;
- dados sejam auditados posteriormente.

---

# 12. SEPARAÇÃO VISUAL NO RELATÓRIO

O HTML deve diferenciar visualmente:

### DADO REAL
- Badge verde ou borda verde
- Fonte explícita
- "Fonte: [descrição] — [data]"

### ESTIMATIVA
- Badge azul ou borda azul
- "Estimativa baseada em [fonte]"
- Faixa de valores

### PROJEÇÃO
- Badge laranja ou borda laranja
- Disclaimer obrigatório
- Cenário identificado (conservador/moderado/agressivo)
- "Projeção baseada em premissas — não é garantia de resultado"

---

# ============================================================
# FVS7 — POSICIONAMENTO COMERCIAL
# ============================================================

# 13. OBJETIVO

O relatório não deve simplesmente diagnosticar o cliente.

Ele deve demonstrar que a FVS7 é a ÚNICA solução para os problemas encontrados.

A FVS7 deve aparecer como a empresa capaz de reconstruir o site do cliente em Astro, resolvendo TODOS os problemas de uma vez.

---

# 14. POSICIONAMENTO DA FVS7

A FVS7 é uma operação especializada em reconstrução de sites em Astro para conversão.

Capacidades:

- **Reconstrução em Astro:** site moderno, rápido, seguro
- **Google Ads:** aquisição de tráfego qualificado
- **SEO:** captura de demanda orgânica
- **Landing Pages de Alta Conversão:** páginas que convertem
- **CRO:** otimização de taxa de conversão
- **Tracking e Analytics:** GTM + GA4 + dados para decisão
- **Performance:** velocidade que retém visitantes
- **Mobile-first:** 70% do tráfego funciona perfeitamente

Tecnologias:

- Astro (arquitetura moderna)
- Tailwind CSS (design consistente)
- Google Tag Manager (rastreamento)
- Google Analytics 4 (dados)
- Google Ads (aquisição)
- SEO técnico (visibilidade)

NÃO apresentar essas tecnologias como simples lista.

Conectar cada tecnologia a um PROBLEMA que ela resolve.

---

# 15. ASTRO — POR QUE É MELHOR

Quando apresentar a solução, destacar por que Astro é superior:

### VELOCIDADE

- Zero JavaScript por padrão
- Carregamento instantâneo
- 90+ no PageSpeed garantido
- 53% menos abandono que sites lentos

### MOBILE

- Design responsivo desde a concepção
- Funciona em qualquer tela
- Google usa mobile-first indexing
- 70% do tráfego funciona perfeitamente

### SEGURANÇA

- Sem WordPress para hackear
- Sem plugins desatualizados
- Sem vulnerabilidades conhecidas
- Atualizações sem quebrar nada

### SEO

- Renderização no servidor (SSR)
- Google indexa conteúdo completo
- Core Web Vitals impecáveis
- Posicionamento superior

### PERFORMANCE

- Pagespeed 90+ garantido
- Tempo de resposta mínimo
- Experiência fluida em 3G
- Conversão 3x maior que sites lentos

### CONVERSÃO

- CRO integrado desde a concepção
- Formulários otimizados
- CTAs estratégicos
- Copy orientada à ação

---

# 16. NÃO VENDER CORREÇÕES. VENDER RECONSTRUÇÃO.

**NUNCA escrever:**

- "Corrigir o formulário"
- "Otimizar as imagens"
- "Melhorar o title tag"
- "Adicionar CTA"
- "Corrigir o CLS"

**SEMPRE escrever:**

- "Reconstrução completa em Astro"
- "Infraestrutura de crescimento"
- "Site moderno com tracking completo"
- "Landing pages otimizadas para conversão"

**Exemplo de copy:**

> **NÃO:** "Você deveria otimizar as imagens e corrigir o formulário de contato."
>
> **SIM:** "Seu site atual não foi construído para converter. A FVS7 reconstrói seu site do zero em Astro — com velocidade instantânea, mobile perfeito, tracking completo e CRO integrado."

---

# 17. CRO

Apresentar CRO como parte integrante da reconstrução, não como serviço avulso.

**NUNCA:** "Serviço de CRO por R$ X"

**SEMPRE:** "CRO integrado na reconstrução em Astro"

Relacionar com:

- visitante permanece no site
- le conteúdo até o final
- clica no CTA
- preenche formulário
- vira cliente

---

# 18. TRACKING

Apresentar tracking como PRIMEIRO passo da reconstrução.

**NUNCA:** "Instalação de GA4 por R$ X"

**SEMPRE:** "Rastreamento completo integrado na reconstrução"

Relacionar com:

- GA4 → dados de comportamento
- GTM → eventos e conversões
- Conversion Tracking → ROI de campanhas
- Pixel → remarketing

---

# 19. GOOGLE TAG MANAGER

Apresentar GTM como infraestrutura de mensuração que faz parte da reconstrução.

Relacionar:

GTM
→ eventos
→ conversões
→ rastreamento
→ dados confiáveis
→ decisões melhores.

---

# 20. GA4

Apresentar GA4 como ferramenta que faz parte da reconstrução.

Não vender GA4 como simples instalação.

Vender:

"estrutura de mensuração completa que transforma comportamento em informação para tomada de decisão."

---

# 21. INTEGRAÇÃO DOS SISTEMAS

A principal proposta de valor técnica deve ser:

Não tratar:

SEO
Google Ads
Site
CRO
Analytics
GTM

como serviços isolados.

Mostrar que eles formam um sistema integrado na reconstrução em Astro.

Exemplo:

RECONSTRUÇÃO EM ASTRO
↓
VELOCIDADE + MOBILE
↓
SEO NATIVO
↓
LANDING PAGES OTIMIZADAS
↓
CRO INTEGRADO
↓
TRACKING COMPLETO (GTM + GA4)
↓
DADOS PARA DECISÃO
↓
GOOGLE ADS COM ROI
↓
CRESCIMENTO CONTÍNUO

---

# ============================================================
# VENDA CONSULTIVA
# ============================================================

# 22. NÃO VENDER ANTES DO DIAGNÓSTICO

O relatório deve primeiro provar o problema.

Somente depois apresentar a solução.

Estrutura:

1. O que encontramos (problema).
2. Por que isso importa (consequência financeira).
3. Quanto está perdendo (custo de não agir).
4. Concorrentes já estão na frente (comparação).
5. A solução: reconstrução em Astro com a FVS7.

---

# 23. CUSTO DA INÉRCIA

O relatório deve mostrar profissionalmente o custo de não corrigir os problemas.

Não utilizar ameaças.

Não exagerar.

Não criar números.

A apresentação do custo da inércia DEVE seguir o framework AIDA definido na seção #40.

Exemplo:

"Enquanto esta estrutura permanecer dessa forma, cada real investido em aquisição continuará levando usuários para uma experiência que não está preparada para converter."

---

# 24. ESPECIALIZAÇÃO

O relatório deve demonstrar que existe diferença entre:

"ter um site"

e

"ter uma infraestrutura de crescimento em Astro."

### SITE CONVENCIONAL

- presença digital;
- páginas;
- formulário;
- conteúdo;
- sem tracking;
- lento;
- quebra no mobile.

### INFRAESTRUTURA DE CRESCIMENTO (ASTRO + FVS7)

- arquitetura performática;
- velocidade instantânea;
- mobile perfeito;
- SEO nativo;
- landing pages por serviço;
- CRO integrado;
- tracking completo (GA4 + GTM);
- dados para decisão;
- otimização contínua.

A comparação deve ser elegante, sem depreciar concorrentes.

---

# 25. CONEXÃO ENTRE PROBLEMA E RECONSTRUÇÃO

Cada problema relevante deve apontar para a reconstrução em Astro como solução.

PROBLEMA:
Site lento, 53% dos usuários saem em 3 segundos.

SOLUÇÃO:
Reconstrução em Astro — carregamento instantâneo.

PROBLEMA:
70% do tráfego é mobile e o site quebra no celular.

SOLUÇÃO:
Reconstrução em Astro — mobile-first desde a concepção.

PROBLEMA:
Sem GA4, sem GSC, sem dados para decidir.

SOLUÇÃO:
Reconstrução em Astro com tracking completo integrado.

PROBLEMA:
Concorrentes já têm tudo isso.

SOLUÇÃO:
Reconstrução em Astro — você volta a competir em igualdade.

---

# 26. OPORTUNIDADE COMO ARGUMENTO DE VENDA

Cada oportunidade importante deve responder:

### O QUE ESTÁ SENDO PERDIDO?

### POR QUE ESTÁ SENDO PERDIDO?

### QUANTO ESTÁ CUSTANDO?

### CONCORRENTES JÁ TÊM ISSO?

### A SOLUÇÃO É RECONSTRUÇÃO EM ASTRO?

### COMO A FVS7 PODE RESOLVER?

---

# ============================================================
# RELATÓRIO HTML — PADRÃO COMERCIAL
# ============================================================

# 27. O HTML DEVE PARECER UM PRODUTO DA FVS7

O relatório não deve parecer:

- template gratuito;
- relatório automático;
- dashboard genérico;
- auditoria SEO comum.

Deve parecer uma entrega premium de consultoria.

---

# 28. FRONTEND SKILL

Antes de criar o HTML:

PROCURAR as skills de frontend/UI disponíveis no ambiente.

Se existir uma skill apropriada:

UTILIZAR OBRIGATORIAMENTE.

Seguir suas regras de:

- design;
- layout;
- responsividade;
- componentes;
- tipografia;
- acessibilidade;
- estrutura visual.

---

# 29. IDENTIDADE FVS7

Usar os dados institucionais oficiais disponíveis.

Nunca inventar:

- logo;
- telefone;
- email;
- endereço;
- URL;
- nome;
- serviços;
- números;
- resultados.

Se existir material oficial de branding no ambiente:

utilizar como fonte.

---

# ============================================================
# PROJEÇÕES FINANCEIRAS — QUANTIFICAR O IMPACTO
# ============================================================

# 30. QUANTIFICAR O IMPACTO EM TERMOS FINANCEIROS

O relatório deve, sempre que possível, transformar problemas técnicos em consequências financeiras.

NÃO basta dizer "seu site é lento".

O cliente precisa entender:

"Seu site demora X segundos para abrir. 53% dos usuários saem após 3 segundos. Com 1.000 visitas/mês, isso representa 530 potenciais clientes perdidos todos os meses."

---

# 31. FUNIL FINANCEIRO

O relatório deve apresentar um funil financeiro quando houver dados suficientes:

INVESTIMENTO EM MÍDIA
→ CPC MÉDIO
→ CLIQUES POR MÊS
→ TAXA DE CONVERSÃO (LP)
→ LEADS QUALIFICADOS
→ TAXA DE FECHAMENTO
→ NOVOS CLIENTES
→ TICKET MÉDIO
→ RECEITA POTENCIAL

Cada etapa deve:

- utilizar dados reais quando disponíveis;
- utilizar estimativas de mercado quando não houver dados;
- identificar claramente o que é real e o que é estimativa;
- mostrar o cálculo transparente.

---

# 32. TICKET MÉDIO

O ticket médio NUNCA deve ser inventado.

Quando não disponível diretamente do cliente:

1. Usar faixas de mercado
2. Criar cenários por serviço
3. Calcular ticket médio ponderado
4. Explicitar que é estimativa de mercado

---

# 33. CENÁRIOS FINANCEIROS

O relatório deve apresentar múltiplos cenários quando houver projeções:

### CONSERVADOR
- Investimento menor
- Taxas de conversão mais baixas
- Resultado potencial mais modesto

### MODERADO
- Investimento intermediário
- Taxas de conversão realistas
- Resultado potencial equilibrado

### AGRESSIVO
- Investimento maior
- Taxas de conversão otimistas
- Resultado potencial maior

Para cada cenário, mostrar:

- investimento necessário;
- volume de cliques;
- leads gerados;
- clientes convertidos;
- receita potencial;
- ROI estimado.

---

# 34. CUSTO DE NÃO AGIR — FRAMEWORK AIDA

⚠️ **REGRA ABSOLUTA:** Esta seção é a mais comercialmente estratégica de todo o relatório. Ela deve conduzir o cliente do diagnóstico à urgência de ação. Usar framework AIDA com tom urgente, consultivo e baseado em evidências.

---

## 34.1. OBJETIVO

Transformar dados técnicos em consequências financeiras tangíveis.

O cliente deve ler esta seção e pensar:

> "Cada dia que passo sem resolver isso, estou perdendo dinheiro."

E depois:

> "Preciso agir agora, não daqui a 3 meses."

---

## 34.2. ESTRUTURA AIDA

### A — ATTENTION (ATENÇÃO)

**Função:** Quebrar a resistência inicial com um dado ou pergunta que gere impacto imediato.

**Técnicas:**

1. **Pergunta provocativa** — direta, sem rodeios:
   - "Quanto da demanda disponível para os seus serviços está sendo capturada hoje?"
   - "Seu site está convertendo visitantes em clientes ou apenas recebendo tráfego?"
   - "Quando foi a última vez que você verificou quantos leads estão sendo perdidos por mês?"

2. **Dado de impacto** — usar dado real da auditoria quando disponível:
   - "Seu site não possui GA4. Você não sabe quantas pessoas o visitam."
   - "Seu site demora X segundos para abrir. 53% dos usuários saem."
   - "70% do seu tráfego é mobile e o site quebra no celular."

3. **Comparação com concorrentes** — quando houver dados:
   - "Enquanto isso, [Concorrente X] já possui GA4 + GSC + Conversion Tracking."

**Regras:**
- NUNCA inventar dados para o gancho. Se não houver dado real, usar pergunta provocativa.
- O gancho deve ser específico ao cliente, não genérico.
- Máximo 2-3 frases antes de transicionar para Interest.

---

### I — INTEREST (INTERESSE)

**Função:** Conectar cada problema técnico a uma consequência financeira real. O cliente deve entender QUEM perde com cada problema.

**Componentes obrigatórios a avaliar:**

| Componente | O que investigar | Consequência financeira |
|---|---|---|
| **Tracking ausente** | GA4/GSC/GTM/Ads não instalados | Decisões no escuro, dinheiro desperdiçado |
| **Velocidade ruim** | Site lento, Core Web Vitals negativos | 53% saem em 3s, 7% perda por segundo |
| **Mobile quebrado** | Layout não funciona no celular | 70% do tráfego vê experiência ruim |
| **Conversão prejudicada** | CTA fraco, formulário problemático | Leads perdidos × ticket médio |
| **Demanda não capturada** | Keywords sem página | Volume × CPC = tráfego perdido |
| **Tráfego pago desperdiçado** | Ads sem tracking, landing page ruim | CPC inflado × cliques = mídia subutilizada |
| **Concorrentes à frente** | Eles têm o que você não tem | Clientes sendo capturados por outros |

**Regra de ouro:** Cada componente DEVE terminar com uma consequência financeira quantificada quando houver dados, ou qualificada quando não houver.

---

### D — DESIRE (DESEJO)

**Função:** Transformar a consequência individual em um custo acumulado que gere urgência real.

**Técnicas:**

#### 34.2.1. MATRIZ DE CUSTO OCULTO

Criar tabela visual expandida com TODOS os componentes:

| # | Componente | O que está acontecendo | Consequência mensal | Acumulado 12 meses | Urgência |
|---|---|---|---|---|---|
| 1 | Tracking ausente | Sem GA4/GSC/GTM | Decisões no escuro | Oportunidade perdida | 🔴 Alta |
| 2 | Velocidade | Site lento em mobile | 53% saem em 3s | Clientes perdidos | 🔴 Alta |
| 3 | Mobile | Layout quebrado | 70% do tráfego waste | Receita perdida | 🔴 Alta |
| 4 | Concorrentes | Eles têm tudo | Clientes saindo | Market share perdido | 🟡 Média |
| ... | ... | ... | ... | ... | ... |

**Classificação de urgência:**
- 🔴 **Alta** — impacto direto em receita, perda diária comprovada
- 🟡 **Média** — impacto indireto, perda acumulável
- 🟢 **Baixa** — melhoria oportunística, pode aguardar

#### 34.2.2. COMPARAÇÃO TEMPORAL — TIMELINE DE PERDA

Criar visual de timeline mostrando acumulação:

```
HOJE ──────────── 30 DIAS ──────────── 90 DIAS ──────────── 12 MESES
  │                  │                     │                      │
  │ Situação atual   │ Perda acumulada     │ Gap aumenta          │ Diferença
  │ Opera assim      │ Já são R$ X         │ Concorrentes         │ pode ser
  │                  │                     │ fortalecem           │ irreversível
```

**Regra:** A timeline deve ser gerada DINAMICAMENTE com base nos dados reais da auditoria. Nunca usar valores fixos.

#### 34.2.3. O CUSTO DA INÉRCIA vs O CUSTO DA AÇÃO

Comparação visual lado a lado:

| MANTER COMO ESTÁ | AGIR AGORA |
|---|---|
| Custo mensal: R$ [X] em oportunidade perdida | Investimento necessário: R$ [Y] |
| Perda acumulada em 12 meses: R$ [Z] | ROI potencial em 12 meses: R$ [W] |
| Concorrentes continuam capturando sua demanda | Posicionamento competitivo recuperado |
| Tráfego pago continua subutilizado | Cada real investido trabalha melhor |
| Decisões baseadas em intuição | Dados reais orientando cada decisão |
| Site lento e quebrado no mobile | Site rápido e perfeito em qualquer tela |

---

### A — ACTION (AÇÃO)

**Função:** Transicionar naturalmente para a seção "A Solução" com clareza sobre o próximo passo.

**Elementos obrigatórios:**

1. **Frase de transição** — conectar custo à solução:
   - "A boa notícia: tudo isso é corrigível com uma reconstrução em Astro."
   - "O investimento para reverter essa situação é significativamente menor do que o custo de não agir."
   - "A FVS7 pode reconstruir seu site e resolver todos esses problemas de uma vez."

2. **Próximo passo claro** — indicar que a seção seguinte mostra o caminho:
   - "Na próxima seção, apresentamos como a reconstrução em Astro resolve cada um desses problemas."

3. **Escassez legítima** — não ameaçadora, mas real:
   - "Concorrentes não estão esperando. Cada dia que passa, eles fortalecem sua presença."
   - "A demanda existe hoje — mas alguém vai capturá-la."

---

## 34.3. REGRAS DE ESCRITA

### TOM

- **Urgente** — não condescendente, não passivo
- **Consultivo** — orientado a resultado, não a medo
- **Específico** — dados reais, não generalizações
- **Honesto** — estimativas claramente identificadas

### NUNCA

- Usar medo artificial ("Você está perdendo milhões!")
- Exagerar números
- Inventar prejuízos
- Criar falsa urgência
- Pressionar emocionalmente sem base factual
- Apresentar estimativas como fatos
- **Listar correções avulsas**
- **Sugerir que o cliente pode fazer sozinho**

### SEMPRE

- Conectar cada dado a uma consequência financeira
- Identificar claramente dado real vs estimativa
- Mostrar premissas quando houver projeção
- Manter credibilidade técnica
- Traduzir linguagem técnica em linguagem de negócio
- **Oferecer reconstrução em Astro como solução**
- **Posicionar a FVS7 como executora**

---

## 34.4. SEPARAÇÃO OBRIGATÓRIA — DADO REAL vs ESTIMATIVA

Cada número nesta seção DEVE possuir badge visual:

- **DADO REAL** → badge verde, fonte explícita
- **ESTIMATIVA** → badge azul, premissas listadas
- **PROJEÇÃO** → badge laranja, disclaimer obrigatório

---

## 34.5. DISCLAIMER OBRIGATÓRIO

Toda projeção DEVE conter:

"Valores representam oportunidade potencial, não faturamento garantido. Projeções baseadas em dados de mercado e premissas explícitas. Dados reais estão identificados com badge verde. Estimativas com badge azul. Projeções com badge laranja."

---

## 34.6. TRANSIÇÃO PARA SEÇÃO 10

A seção "Custo de Não Agir" DEVE terminar com uma frase que conduza naturalmente à seção "A Solução":

"Identificados os custos, o próximo passo é reconstruir sua infraestrutura em Astro. A seção seguinte apresenta como a FVS7 resolve cada um desses problemas de uma vez."

---

## 34.7. CHECKLIST ESPECÍFICO — SEÇÃO 09

Antes de considerar esta seção pronta:

- [ ] Gancho de Attention está presente e usa dado real ou pergunta provocativa
- [ ] Cada componente técnico foi traduzido em consequência financeira
- [ ] Matriz de Custo Oculto está completa com todos os componentes
- [ ] Timeline de perda está presente (30d / 90d / 12 meses)
- [ ] Comparação Inércia vs Ação está presente
- [ ] Todos os números possuem fonte identificada
- [ ] Badges de dado real/estimativa/projeção estão aplicados
- [ ] Disclaimer está presente
- [ ] Transição para seção "A Solução" existe
- [ ] Tom é urgente mas consultivo
- [ ] Nenhum número foi inventado
- [ ] Estimativas estão claramente identificadas

---

# 35. REGRA DE PROJEÇÃO

Projeções são permitidas SOMENTE quando:

1. As premissas estão explicitadas
2. O cenário está rotulado (conservador/moderado/agressivo)
3. O disclaimer está presente
4. Não há mistura entre dado real e projeção sem separação visual
5. A fonte de cada dado utilizado está no DATA_LEDGER

NUNCA apresentar projeção como garantia.

NUNCA apresentar estimativa como dado real.

---

# ============================================================
# ESTRUTURA DO RELATÓRIO — 13 SEÇÕES PAS
# ============================================================

# 36. ESTRUTURA DO RELATÓRIO — 13 SEÇÕES OBRIGATÓRIAS

⚠️ **REGRA ABSOLUTA:** O relatório HTML DEVE conter EXATAMENTE estas 13 seções, seguindo o framework PAS. NENHUMA pode ser omitida.

## CAPA
- "Auditoria de Crescimento Digital"
- Pergunta de impacto: "Quanto da demanda disponível seus concorrentes estão capturando?"
- Nome do cliente, domínio, data, agência

## 01 — VOCÊ ESTÁ PERDENDO (GATILHO: PERDA)
- Card grande: tracking ausente
- Bullet points:
  - ❌ Sem GA4 — não sabe quem visita
  - ❌ Sem GSC — não sabe para quais buscas aparece
  - ❌ Sem GTM — conversões não mensuradas
  - ❌ Sem conversion tracking — ads no escuro
  - ❌ Sem pixel — não consegue remarketing
- Badge: "VOCÊ ESTÁ NO ESCURO"

## 02 — SEUS CONCORRENTES ESTÃO NA SUA FRENTE (GATILHO: COMPARAÇÃO)
- Tabela: Cliente × 4 concorrentes
- Métricas: avaliações, tracking, SEO, Ads, mobile
- Bullet points:
  - Concorrente A: site rápido, mobile perfeito
  - Concorrente B: 47 avaliações vs suas [N]
  - Concorrente C: GA4 + GTM + conversion tracking
  - Concorrente D: landing pages específicas por serviço
- Badge: "ELES JÁ TÊM O QUE VOCÊ NÃO TEM"

## 03 — VELOCIDADE — CADA SEGUNDO É UM CLIENTE (GATILHO: PERDA IMEDIATA)
- Card: "Seu site demora X segundos para abrir"
- Bullet points:
  - 53% dos usuários saem após 3 segundos
  - Cada segundo extra = 7% menos conversão
  - Google penaliza sites lentos
  - Cada real em ads é desperdiçado se o site não abre
- Comparação: Seu site vs benchmark
- Badge: "PERDA DIÁRIA COMPROVADA"

## 04 — MOBILE — SEU SITE É INÚTIL NO CELULAR? (GATILHO: INUTILIDADE)
- Card: "70% das buscas são no celular"
- Bullet points:
  - Layout quebrado em telas pequenas
  - Botões difíceis de clicar
  - Formulário não funciona
  - Texto ilegível
  - Google desconsidera versão desktop para SEO
- Consequência: "70% do seu tráfego está vendo uma experiência ruim"
- Badge: "A MAIORIA DOS SEUS CLIENTES ESTÁ NO CELULAR"

## 05 — O CUSTO DE CADA DIA QUE PASSA (GATILHO: URGÊNCIA)
- Timeline: HOJE → 30d → 90d → 12m
- Bullet points:
  - Cada dia sem dados = decisões no escuro
  - Cada dia sem velocidade = clientes saindo
  - Cada dia sem mobile = 70% do tráfego desperdiçado
  - Cada dia concorrentes fortalecem presença
- Badge: "O CUSTO DA INÉRCIA"

## 06 — ONDE ESTÁ O DINHEIRO SENDO PERDIDO (GATILHO: OPORTUNIDADE)
- Tabela visual:
  - SEO: buscas sendo capturadas por outros
  - Ads: R$ investidos sem tracking
  - Conversão: visitantes saindo sem agir
  - Local: concorrentes com mais avaliações
  - Velocidade: clientes perdidos por lentidão
- Badge: "RADAR DE OPORTUNIDADES"

## 07 — A DEMANDA QUE EXISTE HOJE (GATILHO: ESCASSEZ)
- Keywords com volume e CPC
- Bullet points:
  - "[keyword]" — X buscas/mês — sua página não existe
  - "[keyword]" — concorrentes rankeando
  - "[keyword]" — sua página na página 3
  - "Alguém vai capturar isso. Será você?"
- Badge: "DEMANDA DE MERCADO"

## 08 — O QUE PRECISA SER CORRIGIDO (DIAGNÓSTICO)
- Bullet points por página:
  - Home: sem proposta clara
  - /servico: sem CTA, sem prova
  - /contato: formulário pesado
  - Velocidade: imagens pesadas, scripts lentos
  - Mobile: layout quebrado
- Badge: "DIAGNÓSTICO POR PÁGINA"

## 09 — CENÁRIO FINANCEIRO (GATILHO: VALOR)
- 3 cenários:
  - Conservador: X leads → R$ Y
  - Moderado: X leads → R$ Y
  - Agressivo: X leads → R$ Y
- Disclaimer: "Estimativa baseada em dados de mercado"
- Badge: "PROJEÇÃO FINANCEIRA"

## 10 — A SOLUÇÃO (PAS: SOLUTION)
- **NUNCA listar correções**
- Comparação visual: Site Atual vs Astro + FVS7
- Por que Astro:
  - Velocidade (carregamento instantâneo)
  - Mobile (perfeito em qualquer tela)
  - Segurança (sem vulnerabilidades)
  - SEO (indexação nativa)
  - Performance (Pagespeed 90+)
  - Conversão (CRO integrado)
- O que você recebe:
  - Site reconstruído do zero
  - Landing pages por serviço
  - Tracking completo (GA4 + GTM)
  - SEO técnico impecável
  - Mobile perfeito
  - CRO integrado
- Badge: "RECONSTRUÇÃO COMPLETA EM ASTRO"

## 11 — POR QUE FVS7 (CREDIBILIDADE)
- 5 capacidades conectadas a problemas:
  - Performance (Astro + Tailwind) → site rápido
  - Mobile-first → 70% do tráfego funciona
  - CRO → visitantes viram clientes
  - Tracking (GTM + GA4) → dados para decidir
  - SEO + Ads → demanda capturada
- Badge: "A GENTE SABE RESOLVER ISSO"

## 10 — PLANO: 15 DIAS + 30 DIAS (AÇÃO IMEDIATA)
⚠️ **O plano NÃO é de 90 dias. É de reconstrução imediata.**
- Timeline visual:
  - **Semana 1-2 (15 dias): RECONSTRUÇÃO COMPLETA**
    - Site novo em Astro
    - Todas as páginas de serviço
    - Tracking completo (GA4 + GTM)
    - SEO técnico (sitemap, canonical, schema)
    - Mobile perfeito
    - Formulário de captação
  - **Semana 3-4 (30 dias): ATIVAÇÃO**
    - SEO on-page + conteúdo
    - Google Business Profile
    - Primeiras campanhas Google Ads
    - Landing pages por campanha
    - Conversão de leads
  - **Mês 2+: OTIMIZAÇÃO CONTÍNUA**
    - Análise de dados
    - Otimização de conversão
    - Escala de Ads
    - Conteúdo blog
- Badge: "RECONSTRUÇÃO EM 15 DIAS — ATIVAÇÃO EM 30 DIAS"

## 11 — PRÓXIMO PASSO (CTA)
- "Você já viu o problema. Cada dia que passa é dinheiro sendo perdido."
- Contatos da FVS7:
  - WhatsApp: [número]
  - Email: [email]
  - Site: [URL]
- Capacidades: SEO + Google Ads + CRO + Tracking + Performance
- Badge: "AGENDE UMA CONVERSA AGORA"

---

# 37. REGRA DE NARRATIVA

A narrativa do relatório DEVE seguir o framework **PAS (Problem → Agitation → Solution)**:

PROBLEMA (dados reais)
→ AGITAÇÃO (consequência financeira + comparação com concorrentes + urgência)
→ SOLUÇÃO (reconstrução em Astro com a FVS7)

NÃO:

- Listar problemas técnicos sem conectar a consequências financeiras
- Listar correções avulsas
- Sugerir que o cliente pode fazer sozinho

Cada problema técnico DEVE ser traduzido em:

"Isso significa que [consequência para o negócio]."

E a solução DEVE ser sempre:

"A FVS7 reconstrói seu site em Astro para resolver isso."

---

# 38. CTA DA AGÊNCIA

O CTA final deve enviar o contato para a AGÊNCIA (FVS7), não para o cliente auditado.

WhatsApp: usar número da FVS7
Email: usar email da FVS7
Telefone: usar telefone da FVS7

NUNCA usar dados de contato do cliente no CTA.

## REGRA ABSOLUTA — DADOS DO CTA

A seção de CTA (contato + credibilidade) deve conter EXCLUSIVAMENTE dados da agência (FVS7).

NUNCA utilizar:

- dados do cliente auditado (endereço, telefone, WhatsApp, email);
- estatísticas do cliente (anos de experiência, clientes atendidos, empresas conveniadas);
- números que não sejam da agência;
- métricas que não sejam verificáveis da agência.

A seção de credibilidade/estatísticas deve usar:

- dados verificados da agência;
- ou capacidades/serviços (SEO, Google Ads, CRO, etc.);
- ou tecnologias utilizadas (Astro, Tailwind, GTM, GA4).

Exemplo CORRETO:

"SEO + Google Ads + CRO"
"Astro + Tailwind + Performance"
"GTM + GA4 + Tracking"

Exemplo INCORRETO:

"17 anos de experiência" (dado do cliente)
"850+ clientes atendidos" (dado do cliente)
"22 empresas conveniadas" (dado do cliente)

---

# 45. ESTRUTURA COMERCIAL DO HTML

A estrutura recomendada (PAS-first):

## CAPA

"Auditoria de Crescimento Digital"

Pergunta de impacto

Cliente

Domínio

Data

"Preparado pela FVS7"

---

## 01 — VOCÊ ESTÁ PERDENDO

Tracking ausente → consequence → "Você está no escuro"

---

## 02 — CONCORRENTES À FRENTE

Comparação → consequence → "Eles já têm o que você não tem"

---

## 03 — VELOCIDADE

Velocidade → consequence → "Cada segundo é um cliente perdido"

---

## 04 — MOBILE

Mobile → consequence → "70% do tráfego vê lixo"

---

## 05 — CUSTO DA INÉRCIA

Timeline → consequence → "Cada dia que passa, piora"

---

## 06 — DINHEIRO SENDO PERDIDO

Oportunidades → consequence → "Dinheiro sendo jogado fora"

---

## 07 — DEMANDA QUE EXISTE

Keywords → consequence → "Alguém vai capturar isso"

---

## 08 — DIAGNÓSTICO POR PÁGINA

Problemas → consequence → "Aqui precisa mudar"

---

## 09 — CENÁRIO FINANCEIRO

3 cenários → consequence → "Isso é o que você pode ganhar"

---

## 10 — A SOLUÇÃO

Site Atual vs Astro + FVS7 → "Reconstrução completa — NUNCA correção"

---

## 11 — POR QUE FVS7

5 capacidades → "A gente sabe resolver"

---

## 12 — PLANO 15+30 DIAS

Reconstrução em 15 dias → Ativação em 30 dias → "Ação imediata"

---

## 13 — CTA

Contato FVS7 → "Cada dia que passa é dinheiro perdido. Agende agora."

---

# ============================================================
# FVS7 — SEÇÃO DE VALOR
# ============================================================

# 46. POR QUE A RECONSTRUÇÃO IMPORTA

Depois de demonstrar os problemas, criar uma seção:

"Por que a reconstrução em Astro é a única solução?"

Explicar:

Uma estratégia digital eficiente precisa de:

- arquitetura performática (Astro);
- velocidade (carregamento instantâneo);
- mobile perfeito (70% do tráfego);
- SEO nativo (indexação completa);
- landing pages por serviço (conversão);
- CRO integrado (cada página converte);
- tracking completo (GA4 + GTM);
- dados para decisão (analytics);
- otimização contínua (melhoria).

Isso não é possível com "correções" no site atual.

É preciso reconstruir do zero.

---

# 47. COMO A FVS7 RESOLVE

A FVS7 resolve através de reconstrução completa em Astro.

Capacidades conectadas a problemas:

PROBLEMA: Site lento
→ RECONSTRUÇÃO: Astro com carregamento instantâneo

PROBLEMA: Quebra no mobile
→ RECONSTRUÇÃO: Astro com design responsivo

PROBLEMA: Sem tracking
→ RECONSTRUÇÃO: Astro com GTM + GA4 integrados

PROBLEMA: Conversão baixa
→ RECONSTRUÇÃO: Astro com CRO integrado

PROBLEMA: SEO ruim
→ RECONSTRUÇÃO: Astro com indexação nativa

---

# 48. NÃO VENDER CORREÇÕES. VENDER RECONSTRUÇÃO.

Nunca escrever:

"Corrigir o formulário."

Preferir:

"Reconstrução completa em Astro com formulário otimizado."

Nunca escrever:

"Otimizar as imagens."

Preferir:

"Reconstrução completa em Astro com imagens otimizadas."

Nunca escrever:

"Melhorar o title tag."

Preferir:

"Reconstrução completa em Astro com SEO técnico impecável."

---

# 49. ARGUMENTO DE ESPECIALIZAÇÃO

Quando apropriado, explicar:

"O principal risco não está apenas em continuar com um site que possui problemas. O risco está em investir cada vez mais em aquisição sem reconstruir a infraestrutura que recebe esse tráfego."

Isso deve ser conectado aos dados reais encontrados.

Nunca usar medo artificial.

---

# 50. CTA FINAL

O CTA final deve ser consultivo e enviar o contato para a AGÊNCIA (FVS7), não para o cliente auditado.

Exemplo de estrutura:

"Seu próximo ganho provavelmente não está em gerar mais tráfego.

Está em reconstruir sua infraestrutura para converter melhor.

A FVS7 reconstrói seu site em Astro — com velocidade, mobile, tracking, CRO e SEO integrados."

Depois utilizar o CTA institucional real da FVS7 disponível no sistema.

IMPORTANTE: Os dados de contato (WhatsApp, email, telefone) devem ser da FVS7, NUNCA do cliente auditado.

---

# ============================================================
# QA FINAL — OBRIGATÓRIO
# ============================================================

Antes de entregar o relatório:

## DADOS

[ ] Nenhum número foi inventado.

[ ] Nenhuma métrica foi copiada de memória.

[ ] Nenhuma avaliação GBP foi presumida.

[ ] Todos os números possuem fonte.

[ ] Estimativas estão identificadas.

[ ] Inferências estão identificadas.

## SITE

[ ] O domínio inteiro foi investigado.

[ ] Sitemap foi procurado.

[ ] Todas as páginas importantes foram identificadas.

[ ] A análise não ficou restrita à homepage.

[ ] Páginas comerciais foram analisadas.

## RASTREAMENTO

[ ] GA4 foi detectado/verificado.

[ ] GSC foi detectado/verificado.

[ ] GTM foi detectado/verificado.

[ ] Google Ads foi detectado (se aplicável).

[ ] A ausência de rastreamento foi apresentada como problema de venda.

[ ] A solução de rastreamento foi conectada à reconstrução em Astro.

## VELOCIDADE

[ ] Velocidade foi verificada.

[ ] A velocidade foi apresentada como gatilho de perda.

[ ] A solução de velocidade foi conectada à reconstrução em Astro.

## MOBILE

[ ] Mobile foi verificado.

[ ] O mobile foi apresentado como gatilho de inutilidade.

[ ] A solução de mobile foi conectada à reconstrução em Astro.

## SEO

[ ] OpenSEO foi utilizado quando disponível.

[ ] Keywords relevantes foram pesquisadas.

[ ] Gaps foram identificados.

[ ] Oportunidades foram quantificadas quando possível.

## LOCAL

[ ] GBP foi analisado quando disponível.

[ ] Concorrentes próximos foram analisados.

[ ] Comparação local foi realizada.

## FVS7

[ ] Dados oficiais da agência foram utilizados.

[ ] Astro foi apresentado como solução principal.

[ ] Reconstrução foi apresentada em vez de correções.

[ ] Cada problema foi conectado à reconstrução em Astro.

[ ] A venda dos serviços está fundamentada nos problemas encontrados.

## PAS

[ ] Framework PAS foi seguido (Problem → Agitation → Solution).

[ ] Gatilhos mentais estão presentes (perda, comparação, urgência, escassez).

[ ] **NENHUMA lista de correções avulsas aparece no relatório.**

[ ] **A solução é sempre reconstrução em Astro.**

[ ] **Velocidade é destacada como gatilho de perda.**

[ ] **Mobile é destacado como gatilho de inutilidade.**

## HTML

[ ] Skill de frontend foi procurada.

[ ] HTML é responsivo.

[ ] HTML possui boa hierarquia visual.

[ ] HTML possui identidade FVS7.

[ ] HTML não parece um template genérico.

[ ] CTA final está presente.

[ ] Relatório funciona como material comercial.

Se qualquer item crítico falhar:

NÃO ENTREGAR.

Corrigir primeiro.

# FIM DO PROTOCOLO

# ============================================================
# PROTOCOLO OBRIGATÓRIO — RELATÓRIO HTML RESPONSIVO
# ============================================================

## OBJETIVO

Todo relatório gerado por esta skill é entregue diretamente ao cliente
em formato HTML.

Portanto, o relatório NÃO pode ser tratado como uma página exclusivamente
desktop.

O HTML final deve apresentar aparência profissional, legibilidade e
funcionalidade em:

- smartphones;
- tablets;
- notebooks;
- monitores desktop.

A experiência mobile é obrigatória e deve ser considerada desde a
construção do HTML.

---

# 1. MOBILE-FIRST

O relatório deve ser construído com abordagem mobile-first.

O conteúdo deve funcionar perfeitamente em telas pequenas antes de
ser expandido para telas maiores.

Viewports mínimos obrigatórios para validação:

- 360px;
- 390px;
- 430px;
- 768px;
- 1024px;
- 1440px.

---

# 2. META VIEWPORT OBRIGATÓRIA

O HTML DEVE conter:

<meta name="viewport" content="width=device-width, initial-scale=1.0">

Nunca gerar relatório sem essa configuração.

---

# 3. PROIBIÇÃO DE OVERFLOW HORIZONTAL

O relatório não pode criar scroll horizontal involuntário.

Evitar:

- larguras fixas excessivas;
- elementos maiores que o viewport;
- tabelas estourando o container;
- cards com largura fixa;
- imagens sem limite;
- gráficos com largura fixa;
- textos ou URLs longos quebrando o layout;
- código ou números longos causando overflow.

Utilizar obrigatoriamente quando apropriado:

- width: 100%;
- max-width: 100%;
- box-sizing: border-box;
- overflow-wrap: anywhere;
- word-break: break-word;
- min-width: 0 em elementos flex/grid quando necessário.

---

# 4. CONTAINER RESPONSIVO

O conteúdo principal deve utilizar container fluido.

Exemplo de referência:

.container {
  width: 100%;
  max-width: 1200px;
  margin-inline: auto;
  padding-inline: 16px;
  box-sizing: border-box;
}

Em telas maiores, o padding pode aumentar.

Em telas pequenas, nunca permitir que o padding faça o conteúdo
ultrapassar o viewport.

---

# 5. GRID E CARDS

Cards e grids devem se adaptar automaticamente.

Desktop:
- 2, 3 ou 4 colunas conforme o conteúdo.

Tablet:
- 2 colunas quando apropriado.

Mobile:
- normalmente 1 coluna.

Exemplo:

.grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

@media (max-width: 900px) {
  .grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .grid {
    grid-template-columns: 1fr;
    gap: 14px;
  }
}

Nunca utilizar grids que mantenham várias colunas apertadas em
smartphones apenas para preservar o layout desktop.

---

# 6. TIPOGRAFIA RESPONSIVA

Títulos e textos devem se adaptar ao tamanho da tela.

Evitar títulos enormes em smartphones.

Utilizar, quando apropriado, clamp():

font-size: clamp(1.5rem, 5vw, 2.5rem);

Os textos devem permanecer confortáveis para leitura em telas pequenas.

Não reduzir a fonte a ponto de comprometer a legibilidade.

Referência:

- texto normal: aproximadamente 15–18px em mobile;
- títulos: adaptáveis;
- labels: nunca excessivamente pequenos;
- métricas importantes: destaque visual sem ocupar largura excessiva.

---

# 7. TABELAS

Tabelas são um dos principais pontos de risco do relatório.

Nunca permitir que uma tabela larga quebre o viewport.

Quando houver muitas colunas, envolver a tabela em um container:

.table-wrapper {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

A tabela pode possuir largura mínima interna quando necessário,
mas o scroll deve ocorrer DENTRO do componente e nunca no documento inteiro.

No mobile:

- preservar todas as informações;
- permitir rolagem horizontal apenas dentro da tabela;
- manter cabeçalho identificável;
- evitar colunas ilegíveis;
- considerar transformar tabelas complexas em cards quando isso
  melhorar significativamente a experiência.

---

# 8. GRÁFICOS E VISUALIZAÇÕES

Todos os gráficos devem ser responsivos.

Nunca utilizar dimensões fixas que ultrapassem o viewport.

Imagens, SVGs, canvas e gráficos devem respeitar:

max-width: 100%;
height: auto;

Se utilizar gráficos via JavaScript, o gráfico deve recalcular
suas dimensões conforme o container.

O gráfico não pode:

- ser cortado;
- ultrapassar a tela;
- gerar scroll horizontal;
- possuir legendas ilegíveis no mobile.

---

# 9. IMAGENS

Todas as imagens devem possuir comportamento responsivo.

Regra:

img,
svg {
  max-width: 100%;
}

Imagens não podem ultrapassar seus containers.

Quando apropriado:

height: auto;

Não utilizar imagens gigantes sem necessidade.

---

# 10. KPIs E MÉTRICAS

Cards de métricas como:

- cliques;
- impressões;
- CTR;
- CPC;
- conversões;
- reviews;
- tráfego;
- posições;
- oportunidades;
- valores financeiros;

devem funcionar perfeitamente em mobile.

No desktop podem aparecer lado a lado.

No mobile devem reorganizar-se verticalmente ou em uma grade adequada.

Números grandes não podem provocar overflow.

Exemplo:

1.234.567

R$ 12.497,00

não podem ultrapassar o card.

---

# 11. CTA E BOTÕES

CTAs devem ser facilmente clicáveis em dispositivos móveis.

Evitar botões pequenos ou excessivamente próximos.

Em mobile, quando apropriado:

width: 100%;

ou utilizar uma largura confortável que não prejudique a composição.

Área de toque recomendada:

mínimo aproximado de 44px de altura para elementos interativos.

---

# 12. HEADER E NAVEGAÇÃO

Se o relatório possuir navegação interna, ela deve ser responsiva.

No mobile:

- não permitir menu estourando horizontalmente;
- utilizar navegação empilhada ou menu adaptado;
- permitir acesso fácil às seções;
- não ocupar espaço excessivo.

Se não houver necessidade real de navegação complexa,
preferir uma estrutura simples.

---

# 13. SEÇÕES

Cada seção deve possuir espaçamento responsivo.

Desktop pode utilizar espaçamentos maiores.

Mobile deve reduzir:

- padding;
- margins;
- gaps;
- tamanho de títulos.

Mas nunca sacrificar a hierarquia visual.

O relatório deve continuar parecendo um documento premium no smartphone.

---

# 14. CÓDIGO RESPONSIVO

Preferir:

- CSS Grid;
- Flexbox;
- clamp();
- minmax();
- max-width;
- width: 100%;
- media queries;
- unidades relativas.

Evitar dependência excessiva de:

- posições absolutas;
- larguras fixas;
- alturas fixas;
- coordenadas específicas;
- layouts que só funcionam em uma resolução.

---

# 15. BREAKPOINTS

Utilizar breakpoints coerentes.

Referência:

@media (max-width: 1024px)
@media (max-width: 768px)
@media (max-width: 640px)
@media (max-width: 480px)

Não é necessário utilizar todos.

Utilizar apenas os necessários para manter o layout consistente.

---

# 16. QA VISUAL OBRIGATÓRIO

ANTES de considerar o relatório finalizado, o agente DEVE testar
o HTML em diferentes tamanhos de viewport.

Testar obrigatoriamente:

### Mobile
- 360 × 800
- 390 × 844
- 430 × 932

### Tablet
- 768 × 1024

### Desktop
- 1440 × 900

O teste deve procurar especificamente:

- scroll horizontal inesperado;
- elementos cortados;
- textos sobrepostos;
- cards quebrados;
- tabelas estouradas;
- gráficos cortados;
- imagens fora do container;
- botões inacessíveis;
- títulos quebrados de forma ruim;
- números ultrapassando cards;
- espaçamentos excessivos;
- elementos pequenos demais;
- conteúdo desaparecendo;
- problemas de contraste;
- navegação quebrada.

---

# 17. REGRA DE CORREÇÃO

Se o teste encontrar qualquer problema visual relevante:

1. identificar a causa;
2. corrigir o HTML/CSS;
3. executar novamente o teste;
4. verificar novamente todas as principais larguras;
5. somente então considerar o relatório pronto.

NUNCA entregar conscientemente um relatório com layout quebrado
em dispositivos móveis.

---

# 18. VALIDAÇÃO DE SCROLL HORIZONTAL

O documento inteiro não deve possuir overflow horizontal.

Validar o equivalente a:

document.documentElement.scrollWidth <= window.innerWidth

Se:

document.documentElement.scrollWidth > window.innerWidth

deve ser considerado falha de responsividade, exceto quando o overflow
estiver intencionalmente isolado dentro de componentes como tabelas.

---

# 19. RELATÓRIO PREMIUM EM MOBILE

Responsividade não significa simplesmente "diminuir tudo".

O relatório deve preservar:

- identidade visual;
- hierarquia;
- sensação premium;
- credibilidade;
- leitura executiva;
- destaque dos problemas;
- destaque das oportunidades;
- CTAs;
- apresentação comercial da FVS7.

O mobile deve parecer uma versão cuidadosamente projetada do relatório,
e não uma adaptação improvisada do desktop.

---

# 20. ENTREGA FINAL

Antes de entregar o HTML:

[ ] Meta viewport presente
[ ] Layout mobile-first
[ ] 360px validado
[ ] 390px validado
[ ] 430px validado
[ ] 768px validado
[ ] 1440px validado
[ ] Nenhum overflow horizontal involuntário
[ ] Tabelas responsivas
[ ] Gráficos responsivos
[ ] Imagens responsivas
[ ] Cards responsivos
[ ] KPIs responsivos
[ ] Tipografia responsiva
[ ] CTAs adequados para mobile
[ ] Header/navegação responsivos
[ ] Nenhum elemento cortado
[ ] Nenhum texto sobreposto
[ ] Nenhuma informação importante escondida
[ ] Aparência premium preservada

Somente após todos esses testes o relatório HTML poderá ser considerado
PRONTO PARA ENVIO AO CLIENTE.

# ============================================================
# FIM DO PROTOCOLO DE RESPONSIVIDADE
# ============================================================


# ============================================================
# CORREÇÃO CRÍTICA — TABELAS MOBILE NÃO PODEM SER CORTADAS
# ============================================================

## REGRA ABSOLUTA

O relatório HTML é enviado diretamente aos clientes.

Portanto:

NENHUMA tabela pode exigir que o cliente faça scroll horizontal
para conseguir ler o conteúdo principal.

O uso de:

overflow-x: auto;

NÃO é considerado solução suficiente para tabelas de auditoria.

Se uma tabela não couber confortavelmente em uma tela de smartphone,
ela DEVE possuir uma representação mobile específica.

---

# 1. PROBLEMA A EVITAR

Não gerar tabelas como:

URL | Tipo | Status | Data

mantendo quatro ou mais colunas lado a lado em smartphones.

Isso pode provocar:

- conteúdo cortado;
- colunas parcialmente invisíveis;
- necessidade de arrastar horizontalmente;
- URLs cortadas;
- palavras quebradas de maneira ruim;
- datas divididas;
- badges estreitos;
- relatório visualmente amador.

O cliente deve conseguir ler a informação principal simplesmente
rolando a página para baixo.

---

# 2. COMPORTAMENTO OBRIGATÓRIO

### DESKTOP

Tabelas podem utilizar layout tradicional:

| URL | Tipo | Status | Data |

### MOBILE

A mesma informação deve ser apresentada como cards verticais.

Exemplo conceitual:

┌─────────────────────────────┐
│ URL                         │
│ /tratamentos/endodontia/   │
│                             │
│ Tipo                        │
│ Serviço                     │
│                             │
│ Status                      │
│ Desatualizada               │
│                             │
│ Última atualização          │
│ 2022-06-23                  │
└─────────────────────────────┘

Cada registro deve ocupar a largura disponível.

---

# 3. IMPLEMENTAÇÃO PREFERENCIAL

Quando houver tabelas complexas, o HTML deve permitir uma
apresentação mobile em formato de card.

Uma abordagem recomendada é utilizar atributos:

<td data-label="URL">...</td>
<td data-label="Tipo">...</td>
<td data-label="Status">...</td>
<td data-label="Última atualização">...</td>

No mobile, o CSS pode transformar as células em blocos:

@media (max-width: 640px) {

  table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
  }

  thead {
    display: none;
  }

  tbody,
  tr,
  td {
    display: block;
    width: 100%;
    box-sizing: border-box;
  }

  tbody tr {
    margin-bottom: 14px;
    padding: 14px;
    border-radius: 12px;
    background: #ffffff;
    border: 1px solid rgba(0,0,0,0.08);
  }

  tbody td {
    padding: 7px 0;
    border: 0;
    overflow-wrap: anywhere;
    word-break: break-word;
  }

  tbody td::before {
    content: attr(data-label);
    display: block;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 3px;
    opacity: 0.65;
  }

}

O agente deve adaptar essa técnica ao design visual do relatório.

---

# 4. NÃO USAR TABELA MOBILE QUANDO CARD FOR MELHOR

Para tabelas como:

- páginas do site;
- auditoria de URLs;
- palavras-chave;
- concorrentes;
- problemas encontrados;
- oportunidades;
- recomendações;
- dados de SEO;
- dados de Google Ads;
- dados de GBP;
- tracking;
- comparações;

o agente deve avaliar se a informação será mais fácil de consumir
como cards no smartphone.

Se sim, utilizar cards.

---

# 5. TABELAS PEQUENAS

Tabelas extremamente simples, com poucas colunas e conteúdo curto,
podem continuar como tabela no mobile.

Exemplo:

| Métrica | Resultado |
|---------|-----------|
| CTR     | 4,2%      |
| CPC     | R$ 2,31   |

Mesmo nesses casos:

- nenhuma coluna pode sair da tela;
- nenhum texto pode ser cortado;
- nenhuma célula pode ultrapassar o container.

---

# 6. PROIBIÇÃO DE LAYOUT DESLOCADO

O relatório NÃO pode depender de uma posição horizontal inicial
diferente de zero.

Quando o cliente abre o HTML:

window.scrollX

deve estar efetivamente em:

0

O conteúdo mais importante deve começar alinhado ao lado esquerdo
do container do relatório.

Nunca gerar uma tabela ou componente que faça o navegador abrir
a página visualmente deslocada para a direita.

---

# 7. PROIBIÇÃO DE "SOLUÇÃO" POR SCROLL HORIZONTAL

Não considerar como correção suficiente:

.table-wrapper {
  overflow-x: auto;
}

Essa técnica só pode ser utilizada para informações que
realmente necessitem de visualização tabular horizontal.

Para informações essenciais do diagnóstico:

PREFERIR CARD MOBILE.

---

# 8. URLS

URLs são particularmente perigosas em smartphones.

Nunca permitir que URLs causem:

- expansão da página;
- largura excessiva;
- scroll horizontal;
- quebra visual.

Utilizar:

overflow-wrap: anywhere;
word-break: break-word;

Exemplo:

/tratamentos/cirurgia-dental/

deve permanecer totalmente legível dentro da largura disponível.

Se necessário, a URL pode quebrar em múltiplas linhas.

Isso é preferível a aumentar a largura da página.

---

# 9. BADGES E STATUS

Badges como:

"Desatualizada"
"Indexada"
"Parado desde 2022"
"Serviço"
"Institucional"

devem possuir largura flexível.

Nunca utilizar largura fixa que force:

Desatu
aliza
da

ou:

Servi
ço

quando houver espaço suficiente para apresentar o conteúdo
corretamente.

Utilizar:

display: inline-flex;
max-width: 100%;
white-space: normal;
overflow-wrap: anywhere;

No mobile, quando necessário, o badge pode ocupar a largura
do conteúdo ou tornar-se um elemento de bloco.

---

# 10. DATAS E NÚMEROS

Datas completas devem ser apresentadas de maneira legível.

Evitar que:

2022-
06-23

ocorra quando existe espaço para:

2022-06-23

Valores como:

R$ 12.497,00
1.234.567
4,83%
R$ 2,31

também não podem ser cortados ou quebrados de forma inadequada.

---

# 11. LAYOUT MOBILE DEVE SER REVISADO VISUALMENTE

Depois de gerar o HTML, o agente deve abrir o relatório em:

360px
390px
430px

e procurar especificamente por:

- tabelas cortadas;
- tabelas deslocadas;
- colunas parcialmente visíveis;
- URLs cortadas;
- badges quebrados;
- datas quebradas;
- números quebrados;
- cards ultrapassando a tela;
- headings ultrapassando a tela;
- scroll horizontal;
- conteúdo parcialmente escondido.

Se qualquer um desses problemas aparecer:

NÃO entregar o relatório.

Corrigir e testar novamente.

---

# 12. TESTE DE LARGURA REAL

Além de verificar:

document.documentElement.scrollWidth <= window.innerWidth

também verificar os principais elementos:

- body;
- main;
- section;
- table;
- table-wrapper;
- cards;
- grids;
- imagens;
- SVG;
- canvas;
- headings;
- CTAs.

Nenhum elemento deve possuir largura efetiva maior que o viewport
quando isso não for intencional.

---

# 13. PRINCÍPIO DE EXPERIÊNCIA

O cliente deve conseguir consumir o relatório no celular:

SEM:

- dar zoom;
- arrastar tabela;
- virar o celular obrigatoriamente;
- procurar conteúdo escondido;
- descobrir onde uma coluna continua.

O relatório deve funcionar como uma página web profissional.

A experiência ideal é:

ABRIR → LER → ROLAR → ENTENDER → VER OPORTUNIDADE → CONHECER A SOLUÇÃO → ENTRAR EM CONTATO.

---

# 14. REGRA DE PRIORIDADE

Quando houver conflito entre:

"preservar exatamente o layout desktop"

e

"garantir legibilidade mobile"

PRIORIDADE:

1. Legibilidade
2. Integridade dos dados
3. Responsividade
4. Hierarquia visual
5. Estética
6. Preservação do layout desktop

Nunca sacrificar legibilidade mobile para preservar uma tabela
desktop.

---

# 15. CHECKLIST FINAL ESPECÍFICO PARA TABELAS

Antes de entregar o HTML:

[ ] Nenhuma tabela essencial exige scroll horizontal
[ ] Tabelas complexas possuem versão mobile em cards
[ ] URLs são totalmente legíveis
[ ] Badges não estão sendo quebrados em palavras estranhas
[ ] Datas permanecem legíveis
[ ] Valores financeiros permanecem legíveis
[ ] Cabeçalhos não ultrapassam o viewport
[ ] Nenhuma tabela está deslocada horizontalmente
[ ] Nenhuma informação importante está escondida
[ ] 360px testado
[ ] 390px testado
[ ] 430px testado
[ ] Scroll horizontal global inexistente
[ ] Relatório continua visualmente premium

# ============================================================
# FIM DA CORREÇÃO CRÍTICA DE TABELAS MOBILE
# ============================================================
