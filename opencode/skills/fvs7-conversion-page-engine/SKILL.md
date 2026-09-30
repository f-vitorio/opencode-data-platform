---
name: fvs7-conversion-page-engine
description: 'Sistema central da FVS7 para criar, auditar, reescrever e otimizar páginas web orientadas à conversão. Combina copywriting, CRO, UX de conteúdo, search intent, SEO on-page, arquitetura de informação, oferta, psicologia de consumo, geração e qualificação de leads, performance e acessibilidade. Use quando o pedido for criar uma landing page nova, auditar uma página existente, reescrever uma página ou fazer otimizações incrementais (por exemplo, "crie uma landing page para dentistas", "audit /landing-pages/advogados/", "reescreva a hero").'
---

# FVS7 CONVERSION PAGE ENGINE

## 0. OBJETIVO

Esta skill é o sistema central da FVS7 para **criar, auditar, reescrever e otimizar páginas web orientadas à conversão**.

Ela não é uma "skill de PAS". Ela é um motor de decisão que escolhe a estrutura certa para cada página.

O resultado esperado de toda página produzida ou avaliada por esta skill:

> **relevante para a busca + específica do nicho + clara na oferta + convincente + demonstrável + tecnicamente sólida + orientada à geração de oportunidades.**

---

## 1. PRINCÍPIO FUNDAMENTAL — FRAMEWORKS SÃO FERRAMENTAS

PAS, AIDA, 4Ps, Before-After-Bridge, Storytelling, Problem-Solution, Objection Handling e afins são **ferramentas, não fórmulas**.

A skill escolhe a estrutura mais adequada considerando:

1. URL
2. keyword principal
3. intenção de busca
4. estágio de consciência
5. nicho
6. oferta
7. problema
8. desejo
9. objeções
10. objetivo comercial

**Nunca aplicar uma fórmula de maneira mecânica.**

Se a página estiver seguindo um framework mas não estiver respondendo à intenção do visitante, o framework está errado — não a página.

---

## 2. FILOSOFIA FVS7 — 10 PRINCÍPIOS OBRIGATÓRIOS

### PRINCÍPIO 1 — Search Intent First
A página responde à intenção real do usuário **antes** de tentar vender.

### PRINCÍPIO 2 — Problem Before Product
Nunca começar falando da FVS7. Primeiro demonstrar que entendemos o problema do visitante.

### PRINCÍPIO 3 — Benefit > Feature
Nunca vender tecnologia como benefício.

```text
Feature:    "A página é desenvolvida em Astro."
Benefício:  "Uma estrutura enxuta reduz elementos desnecessários e ajuda a
             entregar uma experiência rápida."
```

### PRINCÍPIO 4 — Demonstrate, Don't Just Claim
Sempre que possível, mostrar visualmente o mecanismo. Se a FVS7 afirma saber criar landing pages, o visitante deve **ver** landing pages. O Showroom FVS7 é peça central dessa estratégia.

### PRINCÍPIO 5 — Proof Before Promise
Nunca inventar clientes, depoimentos, números, resultados, percentuais, avaliações, cases, faturamento ou métricas. Informação indisponível = `[PROOF NEEDED]`.

### PRINCÍPIO 6 — Lead Quality > Lead Volume
O objetivo não é aumentar formulários. É aumentar a quantidade **e qualidade** das oportunidades comerciais.

### PRINCÍPIO 7 — One Primary Conversion
Cada página tem **uma ação principal clara**. CTAs secundários podem existir, mas não competem com o objetivo principal.

### PRINCÍPIO 8 — Clarity Over Cleverness
Preferir clareza, especificidade e relevância a frases criativas que dificultem o entendimento.

### PRINCÍPIO 9 — Every Section Must Have a Job
Toda seção tem função: chamar atenção, contextualizar problema, aumentar relevância, explicar mecanismo, demonstrar solução, provar, reduzir objeção, apresentar oferta ou conduzir CTA. Se uma seção não tem função clara, **questionar sua existência**.

### PRINCÍPIO 10 — Não transformar páginas em clones
Páginas podem compartilhar componentes e princípios. Mas **estratégia, narrativa, dores, desejos, objeções e argumentos são específicos de cada nicho e intenção.**

---

## 3. MODOS DE OPERAÇÃO

A skill opera em quatro modos. O modo é definido pelo comando do usuário ou inferido (ver §28).

| Modo | Função | Altera código? |
|------|--------|----------------|
| **CREATE** | Criar uma página do zero | Sim |
| **AUDIT** | Auditar página existente | **Não** |
| **REWRITE** | Reescrever página existente | Sim (parcial/total) |
| **OPTIMIZE** | Melhoria incremental pontual | Sim (mínimo) |

### Regra de desambiguação
Antes de agir, deixar explícito qual modo foi identificado. Se houver dúvida entre AUDIT e REWRITE (ex.: apenas "analisa `/landing-pages/advogados/`"), **executar AUDIT primeiro** e perguntar se deseja seguir para REWRITE.

**Nunca sobrescrever uma página existente sem entender o pedido.**

---

## 4. WORKFLOW OBRIGATÓRIO (7 FASES)

Toda tarefa de CREATE, REWRITE ou OPTIMIZE segue:

```text
FASE 1 — UNDERSTAND  → entender o pedido (URL, keyword, objetivo, restrições)
FASE 2 — INSPECT     → inspecionar o projeto existente (componentes, rotas, SEO, design)
FASE 3 — STRATEGY    → criar o PAGE STRATEGY MAP (§5)
FASE 4 — COPY        → arquitetura da página + copy + SEO
FASE 5 — IMPLEMENT   → alterar apenas os arquivos identificados
FASE 6 — QA          → build, links, SEO, UX, console, diff (§35)
FASE 7 — REPORT      → reporte no formato §38
```

Em AUDIT, as fases são: UNDERSTAND → INSPECT → EVIDENCE → SEVERITY → REPORT (sem IMPLEMENT/QA).

**Nenhuma fase pode ser pulada.** FASE 3 é obrigatória mesmo para OPTIMIZE de uma única headline: sem estratégia, a mudança é chute.

---

## 5. PAGE STRATEGY MAP

Antes de criar ou reescrever qualquer página, produzir internamente este mapa. Ele controla todo o resto.

```text
URL:
PRIMARY KEYWORD:
SECONDARY KEYWORDS:
SEARCH INTENT:
AUDIENCE:
NICHE:
AWARENESS LEVEL:
CORE PROBLEM:
SECONDARY PROBLEMS:
DESIRED OUTCOME:
EMOTIONAL DRIVERS:
COMMERCIAL DRIVERS:
OBJECTIONS:
MECHANISM:
OFFER:
PRIMARY CTA:
SECONDARY CTA:
AVAILABLE PROOF:
SHOWROOM:
INTERNAL LINKS:
COPY FRAMEWORK:
SEO ANGLE:
CONVERSION GOAL:
```

### Campos obrigatórios
Todos. Quando um campo não tiver informação real disponível, preencher com `[NEEDS INPUT]` ou `[PROOF NEEDED]` — **nunca com uma suposição apresentada como fato**.

### O que o mapa decide
- intenção + awareness → framework de copy (§8)
- objeções → seções de redução de risco (§15)
- proof disponível → o que pode ser afirmado (§16)
- CTA primário → toda a hierarquia de ação da página (§17)
- keyword + ângulo → title, H1, headings, FAQ (§19)

---

## 6. KEYWORD STRATEGY

A skill preserva o foco da URL. A URL define o território; a keyword confirma a promessa.

**Exemplo A**

```text
URL:  /landing-pages/advogados/
PRIMARY KEYWORD:  landing pages para advogados
VARIATIONS:       landing page para advogado
                  landing page para advocacia
                  landing page para escritório de advocacia
```

**Exemplo B**

```text
URL:  /landing-pages/dentistas/
PRIMARY KEYWORD:  landing pages para dentistas
VARIATIONS:       landing page para dentista
                  landing page odontológica
                  landing page para clínica odontológica
```

### Distribuição natural da keyword
Aparecer, quando semanticamente adequado, em:

- title
- H1
- introdução (quando apropriado)
- headings relevantes
- corpo do conteúdo
- FAQ (quando semanticamente adequado)
- meta description
- links internos (anchor natural)

### Anti keyword stuffing
Nunca forçar keyword onde prejudicar a leitura. Se a keyword já cumpriu seu papel no title/H1/um H2, repeti-la nos demais headings é ruído, não otimização.

Se o H1 ficar awkward por causa da keyword exata, usar variação natural que preserve a intenção.

---

## 7. SEARCH INTENT

Classificar a intenção da query principal:

| Tipo | Sinal | Resposta esperada |
|------|-------|-------------------|
| **informational** | "o que é", "como", "guia" | explicar, ensinar |
| **commercial investigation** | "melhor", "vs", "review", "preço de" | comparar, mostrar prova, apresentar oferta |
| **transactional** | "contratar", "orçamento", "landing pages para X" | oferta + CTA imediato |
| **navigational** | nome de marca | encontrar a página exata |
| **local/commercial** + localidade | "em Curitiba", "perto de" | localização + prova local + contato |

### Regra FVS7
Queries comerciais verticais **não** recebem artigo genérico.

`landing pages para advogados` = **página de serviço verticalizada**, não um texto explicando o que é landing page.

Essa página deve responder, em ordem:

1. isso é para mim?
2. vocês entendem meu mercado?
3. como funciona?
4. como é a página? (demonstração)
5. por que essa solução?
6. quanto custa?
7. o que está incluído?
8. como começo?

---

## 8. COPYWRITING ENGINE — SELEÇÃO DINÂMICA DE FRAMEWORK

| Framework | Usar quando |
|-----------|-------------|
| **PAS** | existe um problema comercial claro e o visitante ainda não articulou a solução |
| **AIDA** | é necessário conduzir progressivamente um visitante de baixa consciência |
| **PROBLEM → MECHANISM → SOLUTION** | o visitante já entende o problema e precisa compreender **por que** a solução funciona |
| **OBJECTION → PROOF → OFFER** | a principal barreira naquela região da página é confiança |
| **BEFORE → AFTER → BRIDGE** | é útil mostrar transformação de estado |
| **HYBRID** | combinação é a mais adequada (permitido) |

### Exemplo de híbrido válido

```text
PAS
↓
Solution
↓
Showroom
↓
Mechanism
↓
Proof
↓
Objections
↓
Offer
↓
CTA
```

### Critério de decisão
Escolher o framework que responde melhor à **pergunta que o visitante está fazendo naquele ponto da página** — não o que a skill "prefere".

---

## 9. PAS — REGRA ESPECIAL

PAS **não** significa criar medo artificial.

### Proibido
- terrorismo psicológico
- ameaças e culpa
- urgência falsa
- "você está perdendo milhares de reais"
- "seus concorrentes estão roubando seus clientes"
- qualquer afirmação não comprovada

### Permitido
A agitação **aprofunda o problema de maneira factual e comercialmente relevante**: custo real de inação, consequência verificável, contexto de mercado citado com fonte.

Se a agitação depender de um número inventado para funcionar, **a copy está fraca** — reescreva com um argumento que não exija invenção.

---

## 10. PAGE ARCHITECTURE

Ordem possível de referência:

```text
HERO → PROBLEM → AGITATION → SOLUTION → SHOWROOM → MECHANISM →
BENEFITS → PROOF → PROCESS → OBJECTIONS → OFFER → FAQ → FINAL CTA
```

**Essa ordem NÃO é obrigatória.**

Justificar qualquer mudança. Exemplos legítimos de desvio:

- **Oferta + preço no topo** → quando o preço público é qualificador e a intenção é transactional.
- **Showroom antes do problema** → quando o visitante já tem consciência alta e precisa ver execução, não ser convencido do problema.
- **FAQ antes da oferta** → quando objeções de regra (ex.: OAB, LGPD, prazo) bloqueiam a percepção de viabilidade.
- **Sem seção de problema** → quando a query indica que o visitante já está comprando.

Cada seção precisa de função clara (Princípio 9). Seção sem função = remover.

---

## 11. HERO ENGINE

O Hero responde rapidamente:

1. **O que é?**
2. **Para quem?**
3. **Qual benefício?**
4. **O que fazer agora?**

### Componentes do Hero
- eyebrow (quando útil — não obrigatório)
- H1
- subheadline
- CTA (ação primária)
- apoio visual / captura (formulário, demonstração, prova)

### Regras do H1
- respeitar a intenção da keyword
- não sacrificar clareza por criatividade
- não ser genérico ("Transforme seu negócio digital")
- confirmar a promessa do anúncio quando houver tráfego pago (§27)

### Teste do Hero
Ler apenas o Hero e responder: um desconhecido do nicho diria "isso é para mim" em até 3 segundos? Se não, o Hero falhou.

---

## 12. SHOWROOM ENGINE

O Showroom é parte estratégica da FVS7 (Princípio 4 — Demonstrate).

### Nunca fazer
```text
"Veja nossos modelos."
```

### Sempre fazer
Criar **contexto de demonstração**:

- o que está sendo demonstrado
- para qual nicho
- qual problema a página resolve
- quais elementos de conversão podem ser observados no preview
- CTA para explorar / continuar

### Regra de existência
**Não inventar modelos inexistentes.** Verificar os demos reais disponíveis no projeto antes de referenciar (§33). Se não houver demo para o nicho, usar a seção de demonstração de processo ou remover a seção — não simular um portfólio.

---

## 13. NICHE ENGINE — CADA NICHO É UMA ESTRATÉGIA

Pontos de partida, **não fatos universais**. Adaptar sempre ao contexto real da página e ao briefing recebido.

### ADVOGADOS
área jurídica · autoridade · confiança · busca por especialidade · localização · ética/publicidade (OAB) · contato

### DENTISTAS
procedimento · intenção local · confiança · prova visual · localização · agendamento · urgência quando apropriado

### PSICÓLOGOS
identificação · especialidade · segurança · abordagem · confiança · primeiro contato

### CLÍNICAS
serviços · especialidades · equipe · localização · estrutura · agendamento

### CONTADORES
problema empresarial · necessidade específica · confiança · especialização · diagnóstico · contato

### ARQUITETOS
portfólio · estilo · projeto · autoridade · diferenciação · orçamento

### Como usar
Antes de escrever qualquer seção, perguntar: **esse argumento convenceria alguém desse nicho, ou ele funcionaria igual em qualquer página?** Se funcionaria igual em qualquer página, é genérico → refazer.

---

## 14. OFFER ENGINE

Identificar com clareza:

- o que está sendo vendido
- para quem
- o que está incluído
- investimento (quando disponível)
- condições
- próximos passos
- CTA

### Regras
- não esconder a oferta atrás de excesso de conteúdo
- se houver preço público real, **não remover** só para "aumentar conversão" — preço funciona como filtro de qualificação
- se não houver preço público, tornar explícito o próximo passo de precificação (diagnóstico, orçamento)
- listar entregáveis de forma escaneável (checklist), não em parágrafo denso

---

## 15. OBJECTION ENGINE

Mapear **objeções reais** do nicho/estágio. Exemplos comuns:

- "Já tenho um site."
- "Posso mandar direto para WhatsApp?"
- "Landing page realmente funciona?"
- "Preciso fazer Google Ads?"
- "Quanto custa?"
- "Quanto tempo demora?"
- "Vocês atendem meu nicho?"
- "Posso usar minha identidade visual?"
- "E se eu já tiver uma agência?"

Responder de forma **objetiva e específica**.

**Não criar objeções artificiais para preencher espaço.** Uma FAQ com 8 perguntas que ninguém faz é ruído — e enfraquece as 3 que importam.

---

## 16. PROOF ENGINE

Classificar toda prova disponível antes de escrever:

| Tipo | Exemplos | Limite |
|------|----------|--------|
| **Direct Proof** | cases, resultados, projetos reais | só com dado real verificável |
| **Demonstration Proof** | Showroom, screenshots, previews | sempre que houver ativo real |
| **Process Proof** | metodologia, processo, tecnologia | **nunca** apresentar processo como resultado |
| **Authority Proof** | experiência, certificações, fatos verificáveis | só se verificável |

### Limites
- nunca transformar "processo" em "resultado"
- nunca afirmar que determinada técnica **garante** conversão
- se faltar prova → `[PROOF NEEDED]` ou reescrever sem depender dela

---

## 17. CTA ENGINE

CTA coerente com a intenção e com o estágio do visitante. Deixar claro **o próximo passo**.

### Opções válidas
- Quero minha Landing Page
- Quero criar minha Landing Page
- Ver como funciona
- Solicitar orçamento
- Quero falar com a FVS7
- Quero o diagnóstico gratuito

### Regras
- um CTA primário por página (Princípio 7); secundários secundarizados visualmente
- verbos de ação, primeira pessoa quando possível
- coerência entre CTA e o que acontece depois do clique (formulário, WhatsApp, call)
- repetir o CTA primário em momentos de decisão (pós-prova, pós-oferta, fim da página)
- nunca usar CTA genérico ("Saiba mais", "Enviar") quando existe alternativa mais clara

---

## 18. FORM / LEAD QUALIFICATION

Quando houver formulário, analisar:

- quantidade de campos (cada campo tem justificativa?)
- necessidade de cada campo vs. fricção
- clareza dos labels e placeholders
- privacidade / aviso de uso de dados
- feedback de envio (estado de sucesso/erro)
- próximo passo comunicado após o envio

### Objetivo real do funil

```text
visitante → lead → lead qualificado → oportunidade
```

**Não** apenas `visitante → formulário enviado`.

### Regras
- campos obrigatórios mínimos para qualificar sem matar a conversão
- pedir o que o time comercial realmente usa no primeiro contato
- se o CTA promete algo (diagnóstico, orçamento), o formulário e a confirmação devem entregar exatamente isso
- tracking do formulário precisa existir e estar correto (verificar implementação antes de afirmar que funciona)

---

## 19. SEO ENGINE

Para cada página criada ou reescrita, verificar:

- URL (curta, hierárquica, com a keyword quando natural)
- title (keyword + diferencial, dentro do limite de caracteres)
- meta description (promessa + CTA, dentro do limite)
- canonical
- H1 (um por página) / H2 / H3 com hierarquia lógica
- keyword principal + entidades relacionadas
- conteúdo alinhado à intenção
- links internos contextuais
- breadcrumbs quando apropriado
- FAQ quando apropriado (só com perguntas reais)
- structured data **compatível com o conteúdo real**
- imagens com alt descritivo
- Open Graph
- robots / indexability

### Regra de schema
**Não adicionar schema apenas por adicionar.** Só tipos compatíveis com o conteúdo real da página. Se a FAQ não existe visualmente, não marcar `FAQPage`.

---

## 20. INTERNAL LINKING

Entender a arquitetura real do site antes de sugerir links.

```text
/
↓
/landing-pages/
↓
/landing-pages/advogados/
↓
/landing-pages/advogados/trabalhista/
```

### Regras
- recomendar links internos **contextuais** (onde o âncora ajuda o leitor)
- não criar dezenas de links artificiais
- anchor text natural e relevante — nunca keyword stuffada
- páginas irmãs do mesmo cluster são as melhores âncoras
- verificar que o destino existe antes de linkar

---

## 21. UX/UI COPY

A copy trabalha junto com o layout. Analisar:

- hierarquia visual (o olho encontra a ação?)
- comprimento de blocos de texto
- escaneabilidade (headings, listas, negrito com moderação)
- contraste entre informação e ação
- visibilidade do CTA (inclusive em mobile)
- whitespace
- repetição (mesma ideia dita 3 vezes = ruído)
- densidade de informação
- consistência de tom e termos

### Regra de densidade
Se uma seção precisa de 700 palavras para explicar uma ideia simples, **questionar a estrutura** — o problema quase nunca é a falta de palavras.

---

## 22. ANIMAÇÕES

Não adicionar animações para parecer moderno.

### Uso legítimo
- demonstrar funcionamento
- orientar atenção
- revelar informação
- criar feedback de interação
- destacar interações relevantes
- melhorar compreensão

### Nunca
prejudicar performance, acessibilidade, leitura, CTA ou mobile.

Respeitar `prefers-reduced-motion` quando houver animação.

---

## 23. PERFORMANCE

Filosofia: **performance é parte da experiência de conversão, não argumento absoluto de venda.**

### Proibido afirmar
- "100% de performance garante mais clientes"
- "10 de PageSpeed = mais leads"

### Ao alterar código
- evitar dependências desnecessárias
- preservar Astro (MDX/JS o mínimo possível)
- otimizar imagens
- minimizar JavaScript
- evitar animações pesadas
- preservar Core Web Vitals
- **verificar build**

---

## 24. CLAIM SAFETY

Detectar e sinalizar claims potencialmente problemáticos. Frases como:

- "garante clientes"
- "clientes todos os dias"
- "5x mais conversão"
- "reduz seu CPL em X%"
- "primeiros leads em horas"
- "resultado garantido"
- "100% de compliance"
- "funciona para qualquer negócio"
- "taxa de conversão entre X% e Y%" (quando não há dado próprio verificável)
- "até Nx maior que páginas genéricas" (sem fonte)

### Regra
Só utilizar se houver **evidência específica e verificável**.

Sem prova → substituir por linguagem responsável que preserve a força comercial:

```text
ANTES:  "Sua taxa de conversão será 5x maior."
DEPOIS: "A página é estruturada para reduzir fricção e conduzir o visitante
         até a ação principal — o resultado depende do tráfego e da oferta."
```

Ao auditar, **marcar o claim e a linha**, não apenas "revisar copy".

---

## 25. REGULATORY / NICHE SAFETY

Quando o nicho tiver regras profissionais ou regulatórias, **não inventar interpretações jurídicas**.

### Advocacia (exemplo)
```text
NÃO:  "100% aprovado pela OAB."
OK:   "estrutura desenvolvida considerando as regras aplicáveis à
        publicidade profissional"  (somente quando verdadeiro e com base)
```

Outros nichos com atenção: saúde (CFM/CONTE), psicologia (CRP), contabilidade (CFC), publicidade imobiliária, promessa de resultado em serviços financeiros.

**Dúvida regulatória relevante → sinalizar para revisão humana.** Nunca resolver interpretação de norma por conta própria.

---

## 26. MESSAGE MATCH

Para página criada com tráfego pago, analisar a cadeia:

```text
KEYWORD → AD → HEADLINE → PAGE PROMISE → OFFER → CTA
```

Quanto mais coerente, melhor.

### Exemplo
Anúncio: **"Landing Page para Dentistas"**
A página deve confirmar imediatamente **"Landing Pages para Dentistas"** — não começar falando genericamente de marketing digital.

**A skill não produz landing page genérica quando a intenção é específica.**

---

## 27. FVS7 CONVERSION FRAMEWORK (jornada de referência)

```text
TRAFFIC
↓  message match
RELEVANCE
↓  "é para mim?"
PROBLEM
↓
AGITATION
↓  custo real de inação
SOLUTION
↓
MECHANISM
↓  por que funciona
DEMONSTRATION
↓  Showroom / preview
PROOF
↓
BENEFITS
↓
OBJECTIONS
↓
OFFER
↓
QUALIFICATION
↓  formulário / critérios
CTA
↓
LEAD
```

Não significa que toda página precisa exibir literalmente todos os blocos.

**Significa que a skill deve avaliar se os elementos necessários para mover o usuário pela jornada estão presentes.** Blocos ausentes precisam de justificativa (ex.: "visitante já está no fim do funil, problema não precisa ser reaberto").

---

## 28. DETECÇÃO DE MODO E FONTES DE ENTRADA

### CREATE FROM KEYWORD
```text
Create page:
landing pages para dentistas
```
Inferir:
```text
URL:              /landing-pages/dentistas/
PRIMARY KEYWORD:  landing pages para dentistas
SEARCH INTENT:    commercial
NICHE:            dentistas
CONVERSION:       contratação da FVS7
```
→ executar pipeline completo (§4).

### CREATE FROM URL
```text
Create:
 /landing-pages/dentistas/
```
1. verificar se a página já existe
2. se **não** existir → CREATE
3. se **existir** → perguntar ou inferir se deve ser AUDIT/REWRITE
4. nunca sobrescrever sem entender o pedido

### CREATE FROM BRIEF
```text
Crie uma página para arquitetos.
Keyword: landing pages para arquitetos.
Objetivo: gerar leads.
CTA: solicitar orçamento.
Preço: R$ 2.497.
```
Informações do briefing são **fonte prioritária** sobre qualquer default da skill.

### AUDIT
```text
Audit /landing-pages/advogados/
```

### REWRITE
```text
Rewrite /landing-pages/advogados/ using the FVS7 Conversion Framework.
Preserve the showroom.
```

### OPTIMIZE
```text
Optimize the hero and CTA of /landing-pages/dentistas/
without rebuilding the page.
```

### Sinais de modo

| Frase do usuário | Modo |
|------------------|------|
| "crie", "cria", "nova página", "create" | CREATE |
| "audite", "analise", "revise", "audit", "diagnóstico" | AUDIT |
| "reescreva", "reconstrua copy", "rewrite" | REWRITE |
| "melhore", "otimiza", "ajusta o H1/CTA", "optimize" | OPTIMIZE |
| ambíguo | AUDIT primeiro + perguntar |

---

## 29. MODO CREATE — PIPELINE

1. entender a URL / keyword / objetivo
2. definir keyword principal + variações
3. definir intenção de busca
4. definir público e nicho
5. mapear problema central + secundários
6. mapear desejo / resultado desejado
7. mapear objeções reais
8. definir mecanismo (por que a solução funciona)
9. escolher framework de copy (§8)
10. criar arquitetura de seções com função por seção (§10)
11. escrever copy (Hero → seções → CTA)
12. aplicar SEO (§19) + links internos (§20)
13. implementar reutilizando componentes existentes (§33)
14. QA (§35) + reporte (§38)

---

## 30. MODO AUDIT — SEM ALTERAR CÓDIGO

### Escopo de avaliação
Search Intent · keyword · title · meta · H1 · headings · copy · oferta · CTA · prova · objeções · UX · escaneabilidade · mobile · acessibilidade · links internos · schema · performance · clareza · coerência comercial · message match · formulário/qualificação · claim safety · segurança regulatória.

### Severidade

| Nível | Definição |
|-------|-----------|
| **CRITICAL** | pode prejudicar significativamente a conversão ou a compreensão |
| **HIGH** | problema importante |
| **MEDIUM** | oportunidade de melhoria |
| **LOW** | melhoria incremental |

### Formato de cada achado (obrigatório)

```text
[SEVERIDADE] título curto
PROBLEMA:      o que está errado
POR QUE IMPORTA: impacto na compreensão / confiança / conversão
EVIDÊNCIA:     trecho, linha, URL ou elemento observado
RECOMENDAÇÃO:  correção concreta (com copy sugerida quando aplicável)
IMPACTO ESPERADO: efeito qualitativo esperado — sem número inventado
```

### Regras do AUDIT
- **não inventar dados de conversão**, CTR, taxa ou receita
- separar sempre: fato observado / hipótese / recomendação
- entregar **priorizado** (CRITICAL primeiro), com seção 80/20: o que resolver primeiro
- não alterar nenhum arquivo

### Output do AUDIT
```text
DIAGNÓSTICO          → veredito em 3-5 linhas
CRITICAL             → lista
HIGH                 → lista
MEDIUM               → lista
LOW                  → lista
80/20                → os 3-5 pontos que geram maior impacto
PRÓXIMO PASSO        → AUDIT concluído; sugestão de REWRITE ou OPTIMIZE
```

---

## 31. MODO REWRITE — RECONSTRUIR SEM DESPERDIÇAR

### Antes de editar qualquer linha
1. ler a página **inteira**
2. entender a arquitetura atual (seções e função de cada uma)
3. identificar componentes reutilizáveis
4. identificar keyword
5. identificar intenção
6. identificar elementos existentes
7. identificar **provas reais** disponíveis
8. identificar Showroom
9. identificar CTA
10. criar nova estratégia (PAGE STRATEGY MAP)

### Preservar
- arquitetura técnica saudável
- componentes reutilizáveis
- design system
- identidade visual
- links relevantes
- SEO técnico já correto (canonical, schema válido, breadcrumbs)
- Showroom quando estratégico
- tracking existente e validado

### Alterar
somente o que a estratégia justificar: copy, hierarquia, ordem de seções, oferta, objeções, CTA, ângulo.

**Não reconstruir tudo desnecessariamente.**

---

## 32. MODO OPTIMIZE — MELHORIA INCREMENTAL

Escopo tipicamente: H1, CTA, redução de texto, reorganizar uma seção, melhorar objeções, FAQ, hierarquia, escaneabilidade, conversão.

### Regras
- **não reconstruir a página inteira**
- alterar o menor número de arquivos possível
- cada mudança precisa de justificativa ligada ao PAGE STRATEGY MAP
- manter o resto da página intacto (inclusive o que não está perfeito — está fora de escopo)
- QA obrigatório (§35), ainda que parcial

---

## 33. EXISTING SITE AWARENESS

Antes de criar qualquer página nova, verificar no projeto:

- componentes existentes
- layouts e rotas
- design system (`DESIGN_SYSTEM.md`, `tailwind.config.mjs`)
- header / footer / CTA sticky
- formulários
- Showroom / demos
- páginas relacionadas e clusters
- estilos globais e assets
- SEO existente (titles, schemas, breadcrumbs)
- tracking de conversão

**Não criar uma segunda implementação de algo que já existe.** Reutilizar componentes quando fizer sentido.

### Inventário típico a consultar (projeto FVS7 — `/home/fvitorio/Documents/fvs7`)

```text
Layouts:        src/layouts/BaseLayout.astro, BlogArticle.astro
SEO:            src/components/SEO.astro (title, description, canonical, robots, OG)
Estrutura:      Container, Section, Grid, Card, Breadcrumb, CrossLinks
Formulários:    ServiceForm (variant light/dark, source), ServiceFormExclusivo*,
                SimpleLeadForm, DiagnosticoForm, LeadFunnel
CTA:            StickyCTA, WhatsAppButton, ui/Button, ExitIntentPopup
Conteúdo:       Hero, Problema, Diferenciais, FAQ, PricingTable, TableOfContents
Showroom:       showroom/NicheShowcase (prop `slug`), ShowroomCard, demos/*.astro,
                data/showroom.ts (SHOWROOM_PROJECTS)
UI:             ui/Badge, ui/Button, ui/Card, ui/Input, ui/Link
```

> Confirmar sempre com `ls`/leitura antes de usar. Inventário muda; não assumir.

---

## 34. IMPLEMENTATION RULES

A skill trabalha **em conjunto com o projeto existente**. Prioridades:

1. preservar arquitetura
2. reutilizar componentes
3. evitar dependências novas
4. não quebrar páginas existentes
5. manter consistência visual
6. manter SEO
7. manter performance
8. manter acessibilidade

### Antes de modificar
- listar exatamente quais arquivos serão alterados
- verificar `git status` / diff existente (não sobrescrever trabalho alheio)
- conferir padrões do arquivo vizinho (mesma sintaxe, mesmos tokens de cor, mesmo estilo de comentário de seção)

### Estilo do projeto
- Astro + Tailwind; componentes `.astro` com frontmatter de props
- seções marcadas com comentários `<!-- ===================== NOME — FUNÇÃO ===================== -->`
- classes tokenizadas do design system (`primary-600`, `neutral-950`, `error-500`)

---

## 35. QA OBRIGATÓRIO

Após qualquer implementação:

### Build
```bash
cd /home/fvitorio/Documents/fvs7 && npm run build
```
(`prebuild` roda `scripts/seo-lint.sh` automaticamente — erros de SEO lint contam como falha.)

### Links
Verificar links internos relevantes adicionados/trocados.

### SEO
title · description · H1 · headings · canonical · robots · schema.

### UX
desktop e mobile (mínimo: checar classes responsivas `md:`/`lg:` e overflow).

### Console
Verificar erros quando as ferramentas disponíveis permitirem.

### Código
Revisar diff: só alterações relacionadas ao objetivo. Nenhum conteúdo não relacionado apagado.

### Git
```bash
git diff --stat
```
Não fazer commit sem solicitação.

Se alguma validação não puder ser executada, **informar claramente** que não foi validada.

---

## 36. REGRA DE NÃO-INVENÇÃO (OBRIGATÓRIA)

**Nunca inventar:**

clientes · depoimentos · avaliações · números · resultados · faturamento · percentual de conversão · quantidade de projetos · certificados · prêmios · logos · cases · dados de mercado · estatísticas de busca sem fonte.

### Quando faltar informação
```text
[PROOF NEEDED]
```
ou reescrever com formulação que **não dependa** daquela prova.

### Regra de auditoria de claims
Ao auditar, procurar ativamente claims sem base na página (incluindo componentes compartilhados, ex.: números fixos dentro de formulários) e sinalizá-los em CRITICAL/HIGH conforme o risco.

---

## 37. ESCALABILIDADE — SHARED SYSTEM + UNIQUE STRATEGY

A skill é capaz de criar dezenas de páginas mantendo identidade, qualidade, arquitetura, SEO, componentes e padrões técnicos — **sem gerar clones**.

```text
SISTEMA FVS7 (componentes, design, SEO técnico, QA)
        +
ESTRATÉGIA ESPECÍFICA (dor, desejo, objeção, prova, mecanismo, ângulo)
        =
PÁGINA ÚNICA
```

### Teste anti-clone
Duas páginas de nichos diferentes devem ser distinguíveis **na primeira dobra e no primeiro H2**, mesmo usando o mesmo layout. Se trocar "dentistas" por "advogados" e o texto continuar igual, a página falhou no Princípio 10.

---

## 38. DOCUMENTAÇÃO E EXEMPLOS DE USO

### Comandos suportados

| Modo | Exemplo de comando |
|------|--------------------|
| CREATE | `Create a landing page for dentists. Primary keyword: landing pages para dentistas.` |
| CREATE | `Create: /landing-pages/dentistas/` |
| CREATE (brief) | `Crie uma página para arquitetos. Keyword: landing pages para arquitetos. Objetivo: gerar leads. CTA: solicitar orçamento. Preço: R$ 2.497.` |
| AUDIT | `Audit /landing-pages/advogados/` |
| REWRITE | `Rewrite /landing-pages/advogados/ using the FVS7 Conversion Framework. Preserve the showroom.` |
| OPTIMIZE | `Optimize the hero and CTA of /landing-pages/dentistas/ without rebuilding the page.` |

### Output esperado por modo

**CREATE / REWRITE / OPTIMIZE — FORMATO REPORT**
```text
WHAT CHANGED
WHY
FILES CHANGED
SEO CHANGES
COPY STRATEGY
CONVERSION STRATEGY
QA RESULTS
REMAINING RISKS
```

**AUDIT — §30**
```text
DIAGNÓSTICO → CRITICAL → HIGH → MEDIUM → LOW → 80/20 → PRÓXIMO PASSO
```

### Critérios de decisão (resumo)

| Decisão | Critério |
|---------|----------|
| Qual framework de copy? | pergunta que o visitante faz naquele ponto (§8) |
| Qual a ordem das seções? | função de cada seção + estágio do visitante (§10) |
| Incluir preço? | se público e real → incluir (qualifica) |
| Incluir Showroom? | só com demo real para o nicho (§12) |
| Qual CTA primário? | próximo passo mais claro para o objetivo comercial (§17) |
| Quantos campos no form? | mínimo para qualificar sem matar conversão (§18) |
| Usar este claim? | só com evidência verificável (§24, §36) |
| Reescrever tudo ou otimizar? | tamanho do gap entre estratégia atual e Page Strategy Map |
| Remover seção? | se não tem função clara (Princípio 9) |

---

## 39. REGRA FINAL

A skill **nunca** deve pensar:

> "Como faço essa página parecer mais profissional?"

Ela deve pensar:

> "Como faço essa página responder melhor à intenção do visitante, comunicar o valor da oferta, reduzir incerteza e conduzir o usuário qualificado para a próxima etapa?"

E também:

> "Como demonstro a solução em vez de simplesmente afirmar que ela funciona?"

---

## 40. CHECKLIST DE FECHAMENTO

Antes de entregar qualquer trabalho com esta skill:

- [ ] Modo identificado e comunicado
- [ ] Page Strategy Map completo (ou `[NEEDS INPUT]` explícito)
- [ ] Intenção de busca classificada e respondida
- [ ] H1 confere com keyword + message match
- [ ] Toda seção tem função clara
- [ ] Provas usadas são reais; lacunas marcadas
- [ ] Claims revisados (§24) e conformidade de nicho verificada (§25)
- [ ] Um CTA primário, visível em mobile
- [ ] Formulário avalia qualificação, não só volume
- [ ] SEO checklist completo (§19)
- [ ] Links internos existentes de fato
- [ ] QA executado ou lacuna de QA informada (§35)
- [ ] Nada não relacionado foi alterado
- [ ] Reporte entregue no formato do modo (§38)
