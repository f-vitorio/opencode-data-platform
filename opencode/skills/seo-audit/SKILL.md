---
name: seo-audit
description: Skill de auditoria SEO técnica e on-page. Metodologia sistemática para diagnosticar problemas, classificar severidade e produzir evidências acionáveis.
---

# SEO-AUDIT — Skill de Auditoria SEO

## 1. OBJETIVO

Ensinar o agente a executar auditorias SEO técnicas e on-page de maneira sistemática, com base em evidências observáveis, classificação de severidade e recomendações acionáveis.

Esta Skill não é um checklist genérico. É uma metodologia de diagnóstico.

---

## 2. PRINCÍPIO

Auditoria SEO não é listar 50 itens e marcar "ok/nok".

Auditoria é:

1. Observar o que existe
2. Classificar o que importa
3. Entender por que importa
4. Priorizar o que mudar
5. Explicar o que acontece se não mudar

---

## 3. CLASSIFICAÇÃO DE SEVERIDADE

### CRÍTICO

Impede indexação, causa penalidade ou destrui tráfego existente.

Exemplos:
- robots.txt bloqueando indexação
- redirects em loop
- conteúdo duplicado massivo com canonical errado
- status 500 em páginas importantes
- noindex acidental em páginas que devem ser indexadas

### ALTO

Degrada significativamente o desempenho SEO ou a experiência do usuário.

Exemplos:
- title ausente ou duplicado
- meta description ausente
- H1 ausente ou duplicado
- imagens sem alt text em contexto relevante
- URLs com parâmetros indexáveis
- links internos quebrados em páginas importantes
- schema com erros
- mobile não responsivo

### MÉDIO

Afeta a qualidade SEO mas não é urgente.

Exemplos:
- title muito longo ou muito curto
- headings mal hierarquizados
- conteúdo raso em página comercial
- links internos pouco distribuídos
- imagens pesadas sem compressão
- dados estruturados incompletos

### BAIXO

Melhoria desejável, sem impacto significativo.

Exemplos:
- Open Graph incompleto
- breadcrumbs ausentes
- breadcrumbs com schema incorreto
- metadata de segunda linha
- melhorias de legibilidade

### OPORTUNIDADE

Área onde uma ação pode gerar ganho acima da média.

Exemplos:
- keyword com intenção comercial não explorada
- página órfã com potencial
- concorrente fraco em um segmento específico
- lacuna de conteúdo relevante
- possibilidade de featured snippet

---

## 4. CHECKLIST TÉCNICO

Para cada item, observar, classificar e justificar.

### 4.1 INDEXABILIDADE

- [ ] robots.txt existe e está acessível
- [ ] robots.txt não bloqueia páginas importantes
- [ ] robots.txt referencia sitemap
- [ ] meta robots não contém noindex acidental
- [ ] canonical está definido
- [ ] canonical aponta para a URL correta
- [ ] páginas com status HTTP 200
- [ ] sem redirects desnecessários (máximo 1 cadeia)
- [ ] sem redirects para páginas 404

### 4.2 SITEMAP

- [ ] sitemap.xml existe
- [ ] sitemap.xml é acessível
- [ ] sitemap.xml contém URLs relevantes
- [ ] sitemap.xml não contém URLs 404 ou redirecionadas
- [ ] sitemap.xml segue formato padrão
- [ ] sitemap.xml é referenciado no robots.txt
- [ ] sitemap não excede 50.000 URLs (quando aplicável)

### 4.3 URLs

- [ ] URLs são amigáveis (readable)
- [ ] URLs contêm keyword quando apropriado
- [ ] URLs não possuem parâmetros desnecessários
- [ ] URLs são consistentes (sem trailing slash duplo, etc.)
- [ ] URLs não contêm caracteres especiais
- [ ] URLs têm hierarquia lógica (/servico/subservico/)

### 4.4 HEADINGS

- [ ] H1 existe em cada página
- [ ] H1 é único por página
- [ ] H1 contém a keyword principal quando apropriado
- [ ] hierarquia H1 → H2 → H3 respeitada
- [ ] headings não são saltados (H1 → H3 sem H2)

### 4.5 TITLE E META DESCRIPTION

- [ ] title existe em todas as páginas importantes
- [ ] title é único por página
- [ ] title contém keyword principal
- [ ] title respeita limite de caracteres (~55-60)
- [ ] title é atraente para cliques
- [ ] meta description existe
- [ ] meta description é única por página
- [ ] meta description contém keyword e CTA
- [ ] meta description respeita limite (~150-160)

### 4.6 IMAGENS

- [ ] imagens possuem alt text
- [ ] alt text é descritivo e relevante
- [ ] imagens são comprimidas
- [ ] imagens usam formato moderno quando aplicável (WebP)
- [ ] imagens não são carregadas com lazy loading que prejudique indexação
- [ ] dimensões (width/height) estão definidas para evitar layout shift

### 4.7 LINKS

- [ ] links internos apontam para páginas relevantes
- [ ] links internos não quebrados (status 404)
- [ ] links externos são relevantes e de qualidade
- [ ] links externos possuem rel="noopener" quando necessário
- [ ] links não utilizam JavaScript para navegação básica
- [ ] anchor text dos links internos é relevante

### 4.8 DADOS ESTRUTURADOS

- [ ] schema está presente quando aplicável
- [ ] schema está válido (testar com ferramenta Google)
- [ ] schema contém propriedades obrigatórias
- [ ] schema não contém erros de sintaxe
- [ ] schema está alinhado com o conteúdo da página

### 4.9 PERFORMANCE (quando observável)

- [ ] tempo de carregamento não é excessivo
- [ ] recursos críticos não estão bloqueados
- [ ] JavaScript não impede renderização do conteúdo
- [ ] CSS crítico está inline ou carregado primeiro
- [ ] fonts não bloqueiam renderização

### 4.10 MOBILE

- [ ] viewport meta tag está definida
- [ ] layout é responsivo
- [ ] texto é legível sem zoom
- [ ] botões/links são clicáveis em tela pequena
- [ ] não há conteúdo horizontal overflow

---

## 5. CHECKLIST ON-PAGE

### 5.1 CONTEÚDO

- [ ] página cobre a intenção de busca
- [ ] conteúdo é substantivo (não薄い)
- [ ] conteúdo possui profundidade adequada ao tópico
- [ ] conteúdo é único (não copiado)
- [ ] conteúdo atualizado quando relevante
- [ ] conteúdo escaneável (headings, listas, parágrafos curtos)

### 5.2 ENTIDADES E SEMÂNTICA

- [ ] entidade principal está clara
- [ ] entidades secundárias são relevantes
- [ ] termos relacionados estão presentes
- [ ] não há keyword stuffing
- [ ] conteúdo cobre subtópicos relevantes
- [ ] conteúdo responde a perguntas do público

### 5.3 SINAIS COMERCIAIS

- [ ] CTA está presente
- [ ] proposta de valor está clara
- [ ] diferenciais estão visíveis
- [ ] prova social está presente quando relevante
- [ ] contato está acessível
- [ ] formulário funciona
- [ ] WhatsApp está acessível quando relevante

### 5.4 ALINHAMENTO KEYWORD-PÁGINA

- [ ] keyword principal está no title
- [ ] keyword principal está no H1
- [ ] keyword principal está no primeiro parágrafo
- [ ] keyword está distribuída naturalmente no conteúdo
- [ ] a página é a mais relevante para a keyword (não há canibalização)

---

## 6. CRITÉRIOS DE AVALIAÇÃO

Para cada problema encontrado, documentar:

### 6.1 LOCALIZAÇÃO

- URL exata
- Elemento específico (tag, atributo, trecho)

### 6.2 EVIDÊNCIA

- O que foi observado
- Como foi verificado
- Por que é um problema

### 6.3 IMPACTO

- Impacto na indexação
- Impacto no ranqueamento
- Impacto na experiência do usuário
- Impacto na conversão

### 6.4 RECOMENDAÇÃO

- O que deve ser feito
- Como deve ser feito
- Dependências

### 6.5 ESFORÇO

- Fácil (menos de 1 hora)
- Médio (1-4 horas)
- Complexo (mais de 4 horas)
- Estrutural (requer mudança de arquitetura)

---

## 7. LIMITAÇÕES

A Skill de auditoria NÃO pode:

- acessar Google Search Console
- acessar Google Analytics
- acessar dados de backlinks de ferramentas pagas
- medir Core Web Vitals com precisão (a menos que o usuário forneça)
- acessar dados de tráfego
- verificar posicionamento exato no Google
- acessar dados de usuários
- testar formulários internamente
- verificar velocidade de servidor com precisão

Quando não for possível avaliar algo, declarar:

> "Não foi possível avaliar [item] sem acesso a [ferramenta/dado]. Recomendação: verificar manualmente ou fornecer os dados."

---

## 8. FORMATO DE SAÍDA DA AUDITORIA

Para cada seção, usar:

### PROBLEMA

Descrição do que foi encontrado.

### EVIDÊNCIA

Como foi verificado. O que foi observado.

### IMPACTO

Por que importa. O que pode acontecer.

### RECOMENDAÇÃO

O que fazer. Como fazer.

### SEVERIDADE

CRÍTICO | ALTO | MÉDIO | BAIXO | OPORTUNIDADE

### ESFORÇO

Fácil | Médio | Complexo | Estrutural

---

## 9. REGRA FINAL

Uma auditoria SEO sem priorização é inútil.

O cliente não precisa saber de 47 problemas. Ele precisa saber:

1. O que está impedindo resultados
2. O que pode gerar mais resultado com menos esforço
3. O que fazer primeiro
4. Por quê

Priorizar por impacto comercial, não por volume de problemas.
