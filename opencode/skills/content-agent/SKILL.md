# Content Agent — FVS7

Agente autônomo de conteúdo que gera posts para o blog, agenda redes sociais e publica automaticamente.

## Quando usar

- Usuário pede para criar um artigo/blog post
- Usuário pede para gerar conteúdo de marketing/vendas
- Usuário quer automatizar publicações
- Tarefa de criar conteúdo para SEO

## Fluxo completo

### 1. Gerar conteúdo do artigo

Use o script `scripts/blog/blog_generator.py` para criar o artigo `.astro`:

```bash
python3 scripts/blog/blog_generator.py \
  --title "Título do Artigo" \
  --category "Marketing" \
  --description "Descrição curta para SEO (150-160 chars)" \
  --keywords "keyword1, keyword2, keyword3" \
  --h1 "Título Principal H1" \
  --subtitle "Subtítulo explicativo" \
  --content-file /tmp/content.html \
  --faqs '[["Pergunta 1?", "Resposta 1."], ["Pergunta 2?", "Resposta 2."]]'
```

### 2. Conteúdo do artigo

O conteúdo deve ser HTML e seguir este padrão:

```html
<h2>Seção Principal</h2>
<p>Parágrafo com conteúdo relevante, dados e estatísticas.</p>

<h3>Subseção</h3>
<ul>
  <li><strong>Ponto 1:</strong> Explicação</li>
  <li><strong>Ponto 2:</strong> Explicação</li>
</ul>

<blockquote>
  <p>Citação ou dado de destaque.</p>
</blockquote>

<h2>Próxima Seção</h2>
<p>Conteúdo...</p>
```

### 3. Regras de conteúdo

- **Idioma:** Português do Brasil
- **Tom:** Profissional, direto, baseado em dados
- **Tamanho:** 1500-3000 palavras
- **Estrutura:** H2 para seções, H3 para subseções
- **Dados:** Incluir estatísticas e números reais quando possível
- **CTA:** Sempre terminar com chamada para ação
- **SEO:** Title < 60 chars, description 150-160 chars
- **FAQ:** 3-5 perguntas relevantes com respostas diretas

### 4. Temas permitidos

O conteúdo deve ser sobre:
- Marketing digital
- Google Ads
- Landing pages
- CRO (Conversion Rate Optimization)
- SEO
- Vendas B2B
- Gestão de tráfego
- Marketing para nichos (clínicas, advogados, contadores, etc.)

### 5. Após criar o artigo

1. Verificar se o arquivo foi criado: `ls src/pages/blog/{slug}.astro`
2. Atualizar o index se necessário
3. Criar posts para redes sociais:
   - 1 post LinkedIn (técnico, com dados)
   - 1 post GBP (com telefone)
4. Commit e push:
   ```bash
   git add src/pages/blog/ src/pages/blog/index.astro
   git commit -m "feat(blog): novo artigo - {título}"
   git push
   ```

### 6. Agenda de conteúdo

O agente pode gerar conteúdo para:
- **Terça-feira:** Artigo sobre marketing/vendas
- **Sexta-feira:** Artigo sobre Google Ads/CRO

### 7. Exemplo de uso

```
Usuário: Crie um artigo sobre "Como Escolher Agência de Marketing"
```

Executar:
```bash
python3 scripts/blog/blog_generator.py \
  --title "Como Escolher Agência de Marketing: Guia Completo" \
  --category "Estratégia" \
  --description "Como escolher agência de marketing digital. Critérios, perguntas, erros comuns e checklist para tomar a decisão certa." \
  --keywords "escolher agência de marketing, agência de marketing digital, como escolher agência" \
  --h1 "Como Escolher Agência de Marketing: O Guia Definitivo" \
  --subtitle "Descubra os critérios essenciais para escolher a agência de marketing certa para o seu negócio." \
  --content-file /tmp/article-content.html \
  --faqs '[["O que uma agência de marketing faz?", "Uma agência de marketingdigital oferece serviços como gestão de Google Ads, criação de landing pages, SEO, marketing de conteúdo e análise de dados para gerar leads e vendas."], ["Quanto custa contratar uma agência?", "O custo varia de R$1.500/mês (freelancer) a R$15.000+/mês (agência completa). O investimento depende do escopo, canal e tamanho da operação."], ["Como saber se a agência é boa?", "Verifique cases reais, peça referências, analise os resultados próprios da agência (site, Google Ads, SEO), e avalie a transparência no communicate."]]'
```

## Scripts relacionados

- `scripts/blog/blog_generator.py` — Gerador de artigos .astro
- `scripts/backlinks/buffer_auto_schedule.py` — Agendador Buffer
