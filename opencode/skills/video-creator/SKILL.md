---
name: video-creator
description: Cria vídeos profissionais verticais (9:16) para FVS7 Growth com identidade visual, narração ElevenLabs, imagens do Pexels e legendas queimadas. Use para criar Reels, TikTok, YouTube Shorts e Stories.
---

# VIDEO CREATOR FVS7

## OBJETIVO

Criar vídeos verticais profissionais para a FVS7 Growth com:
- Identidade visual consistente
- Narração com voz profissional (ElevenLabs)
- Imagens relevantes do Pexels
- Legendas queimadas
- CTA com URL do site

## QUANDO USAR

- Criar Reels/TikTok/Shorts sobre marketing digital
- Criar vídeos explicativos sobre Google Ads, SEO, Landing Pages
- Criar vídeos de prova social ou depoimentos
- Criar vídeos de oferta para serviços da FVS7
- Criar conteúdo educativo sobre tráfego pago

## REGRAS OBRIGATÓRIAS

### Regra 1: Imagens
- **USAR SOMENTE** imagens relacionadas a: marketing digital, SEO, Google Ads, YouTube Ads, analytics, dashboards, laptops, escritórios, reuniões de negócio
- **NÃO USAR** imagens de: financeiro/bolsa, comida, natureza, pessoas aleatórias, esportes, viagens
- **NÃO USAR** imagens que contenham logos, referências ou qualquer elemento do Instagram, Facebook ou Meta
- Queries de busca DEVE conter termos como: `marketing`, `digital`, `analytics`, `dashboard`, `laptop`, `office`, `advertising`, `business`

### Regra 2: Voz
- **OBRIGATÓRIO** usar edge-tts com voz masculina profissional `pt-BR-AntonioNeural`
- **NÃO USAR** vozes femininas, infantis ou desconhecidas
- Tom profissional, claro e articulado
- Nunca substituir a voz sem autorização explícita do usuário

### Regra 3: Melhorias
- Quando o usuário solicitar melhorias em um vídeo existente, **APENAS CORRIGIR** o vídeo atual
- **NÃO CRIAR** novas versões (v2, v3, etc.)
- Sobrescrever o arquivo original com as correções
- Manter o mesmo nome de arquivo

## IDENTIDADE VISUAL

### Cores
```
PRIMÁRIA: #1a1a2e (azul escuro - fundo)
SECUNDÁRIA: #16213e (azul marinho)
DESTAQUE: #0f3460 (azul médio)
ACENTO: #e94560 (vermelho/alaranjado - CTA)
TEXTO: #ffffff (branco)
AMARELO: #FFD700 (URL do site)
```

### Tipografia
- Títulos: Negrito, sombra escura
- Corpo: Regular, borda preta
- URL: Amarelo (#FFD700), sem borda

### Elementos
- **Meio**: Texto do roteiro (branco, 48px, sombra)
- **Inferior**: "FVS7 MARKETING DIGITAL" (branco, 32px) + "www.fvs7.com.br" (amarelo, 36px) - ambos centralizados na parte inferior

## FLUXO DE TRABALHO

### 1. Criar Roteiro
```
Estrutura por segmento:
- 1-2 frases curtas
- Máximo 26 caracteres por linha
- Tom: direto, benefício, ação
- Foco: problema → solução → CTA
```

### 2. Buscar Imagens (Pexels)
**REGRA OBRIGATÓRIA**: Usar SOMENTE imagens de marketing/digital/analytics

Queries permitidas (usar apenas estas ou similares):

| Categoria | Query Permitida |
|-----------|-----------------|
| Marketing | `social media marketing instagram facebook laptop smartphone` |
| Google Ads | `google ads advertising campaign laptop screen website` |
| SEO | `seo search engine optimization website google ranking laptop` |
| Landing Pages | `landing page website conversion funnel form laptop` |
| Gestão de Tráfego | `paid traffic advertising campaign google ads website laptop` |
| Conversão | `conversion rate optimization cta form website laptop` |
| Leads | `lead generation crm form contact website laptop` |
| Analytics | `website analytics performance metrics google laptop` |

**NÃO USAR** queries como: financeiro, bolsa, revenue, stock, trading, investment

### 3. Gerar Narração
**Regra 2**: Usar edge-tts com voz masculina profissional

```python
VOICE = "pt-BR-AntonioNeural"  # Voz masculina profissional
```

Configurações recomendadas:
- Rate: +15% (ritmo comercial mais ágil)
- Volume: +0%
- Pitch: +0Hz

### 4. Montar Vídeo
- Formato: 1080x1920 (9:16)
- FPS: 30
- Codec: H264 + AAC
- Ken Burns: zoom_in, zoom_out, pan_left, pan_right
- Fade: 0.4s entrada/saída

## COMANDOS

### Gerar vídeo com narração
```bash
cd ~/video-maker
source venv/bin/activate

# Com imagem específica
python make_video.py \
  --file roteiro.txt \
  --audio \
  --search-images \
  --search-query "QUERY ESPECÍFICA AQUI" \
  --page-url "https://fvs7.com.br/landing-pages/clinicas/" \
  --output ~/Videos/video-maker/nome_video.mp4

# Com áudio customizado
python make_video.py \
  --file roteiro.txt \
  --audio caminho/audio.mp3 \
  --search-images \
  --search-query "QUERY" \
  --page-url "https://fvs7.com.br/landing-pages/clinicas/" \
  --output output.mp4
```

### Parâmetros importantes
- `--file`: Arquivo de roteiro (.txt)
- `--audio`: Ativa narração ElevenLabs (sem argumento) ou usa áudio customizado
- `--search-images`: Busca imagens no Pexels
- `--search-query`: Query de busca para imagens (IMPORTANTE: usar query específica de marketing/digital/analytics)
- `--page-url`: URL específica da página para aparecer na descrição do vídeo (ex: https://fvs7.com.br/landing-pages/clinicas/)
- `--output`: Caminho de saída
- `--images`: Imagens próprias (DEVE seguir as regras de imagem da skill - sem logos do Instagram/Facebook/Meta)

### Saída Gerada
1. **Vídeo**: Arquivo .mp4 com identidade visual FVS7
2. **Metadados**: Arquivo .txt com título SEO, descrição e hashtags (contendo a URL específica da página se fornecida)
3. **Checklist**: Lista de verificação para publicação

### Exemplo de Saída
```
Vídeo:  ~/Videos/video-maker/clinicas_v7.mp4
Duração:  79.3s

TÍTULO SEO:
  Landing Page para Clínicas: Converta Mais Agendamentos

DESCRIÇÃO salva em: ~/Videos/video-maker/clinicas_v7.txt
```

## TÍTULOS E DESCRIÇÕES SEO

### Regra de Ouro: Título Vencedor (Shorts)
**Template obrigatório**: `[Nicho]: [Número/Resultado] + [Benefício] + [Google Ads/Keyword]`

**Exemplos validados** (taxa de cliques alta):
- "Clínica de Estética: 50 Agendamentos/Mês com Google Ads"
- "Contadores: 3x Mais Leads PJ com Google Ads"
- "Fisioterapeutas: Agenda Cheia em 30 Dias"
- "Negócio Local: Clientes da Rua em 7 Dias com Google Ads"

**Por que funciona**:
1. **Nicho primeiro** → YouTube identifica o público-alvo imediatamente
2. **Número específico** → Gera curiosidade e credibilidade
3. **Benefício claro** → O que o espectador vai ganhar
4. **Keyword de alta intenção** → "Google Ads", "Landing Page", "Leads"

### Regras para Títulos
| Regra | Correto | Errado |
|-------|---------|--------|
| Máximo 50 caracteres | "Contadores: 3x Mais Leads PJ" | "Como os Contadores Podem Atrair Mais Clientes Usando Google Ads" |
| Nicho primeiro | "Psicólogos: Agenda Cheia" | "Dicas de Marketing para Psicólogos" |
| Número específico | "50 Agendamentos/Mês" | "Muitos Agendamentos" |
| Sem perguntas no início | "Sua LP Perde Clientes?" ❌ | "Auditoria Grátis: Sua LP Perde Clientes?" ✅ |
| Palavras de impacto | "Queimando dinheiro", "3x mais" | "Melhorar resultados" |

### Regras para Descrições
1. **Primeira linha** = Título + keyword do nicho (YouTube lê os primeiros 150 chars)
2. **Segunda linha** = Gancho de curiosidade ou dor
3. **Timestamps** = Opcional mas recomendado para vídeos >30s
4. **CTA claro** = Link com UTM para diagnóstico grátis
5. **Hashtags** = Máximo 5, incluir #Shorts sempre
6. **SEM newlines problemáticos** = YouTube API rejeita descrições com \n duplicados

### UTMs para Rastreamento GA4
**OBRIGATÓRIO**: Todo link na descrição DEVE conter UTMs para rastreamento no GA4.

**Estrutura de UTM**:
```
fvs7.com.br/diagnostico-gratuito
  ?utm_source=youtube
  &utm_medium=shorts
  &utm_campaign={VIDEO_ID}
  &utm_content={NICHE}
```

**Parâmetros**:
| UTM | Valor | Exemplo |
|-----|-------|---------|
| `utm_source` | `youtube` | Fixo |
| `utm_medium` | `shorts` | Fixo para Shorts |
| `utm_campaign` | `{VIDEO_ID}` | `ds8O7QfE6EA` |
| `utm_content` | `{NICHE}` | `clinicas`, `contadores`, `advogados` |

**Nomes de nicho para utm_content**:
- `clinicas` — clínicas de estética, dermatologia, etc.
- `advogados` — marketing jurídico
- `contadores` — contabilidade, PJ
- `fisioterapeutas` — fisioterapia
- `psicologos` — psicologia, terapia
- `imobiliarias` — imobiliárias, corretores
- `esteticistas` — estética, beleza
- `negocios_locais` — negócios locais, comércio
- `marketing` — marketing digital geral
- `landing_pages` — CRO, conversão
- `tracking` — GA4, GTM, métricas

**Exemplo de descrição com UTM**:
```
Contadores: 3x Mais Leads PJ com Google Ads

Contadores: Como Atrair Clientes PJ de Forma Previsível

3 motivos pelos quais contadores perdem dinheiro no Google Ads:
1. Copy genérica que não diferencia
2. Orçamento dividido entre 10 serviços
3. Falta de prova social

Framework de 3 etapas:
1. Ofereça "Diagnóstico Tributário Grátis"
2. Use números: "R$47k economizados para PJ"
3. Prova social: depoimentos reais

👉 Diagnóstico Grátis: fvs7.com.br/diagnostico-gratuito?utm_source=youtube&utm_medium=shorts&utm_campaign={VIDEO_ID}&utm_content=contadores

#GoogleAds #Contabilidade #MarketingDigital #FVS7 #Shorts
```

### Hashtags Recomendadas por Nicho
- **Clínicas**: #GoogleAds #Clínica #Estética #Agendamento #Shorts
- **Advogados**: #Advogado #MarketingJurídico #ClientesPremium #Shorts
- **Contadores**: #Contador #Contabilidade #LeadsPJ #Shorts
- **Fisioterapeutas**: #Fisioterapia #Pacientes #Clínica #Shorts
- **Psicólogos**: #Psicologia #Terapia #Pacientes #Shorts
- **Negócios Locais**: #NegócioLocal #GoogleMeuNegócio #Shorts
- **Marketing**: #MarketingDigital #TráfegoPago #LandingPage #CRO #Shorts

### Erros Comuns (NÃO FAZER)
- ❌ Título genérico: "Dicas de Marketing Digital"
- ❌ Pergunta no início: "Você sabia que...?"
- ❌ Sem nicho: "Como Ganhar Mais Clientes"
- ❌ Muito longo: "Aprenda Como Fazer Google Ads Para Sua Empresa E Atrair Mais Clientes"
- ❌ Descrição com \n\n\n (YouTube rejeita)

### Exemplo de Descrição Correta (SEO)
```
Contadores: 3x Mais Leads PJ com Google Ads

Contadores: Como Atrair Clientes PJ de Forma Previsível

3 motivos pelos quais contadores perdem dinheiro no Google Ads:
1. Copy genérica que não diferencia
2. Orçamento dividido entre 10 serviços
3. Falta de prova social

Framework de 3 etapas:
1. Ofereça "Diagnóstico Tributário Grátis"
2. Use números: "R$47k economizados para PJ"
3. Prova social: depoimentos reais

Google Ads para contadores: como funciona.
SEO para contâbeis: como aparecer no Google.

#GoogleAds #Contabilidade #MarketingDigital #FVS7 #Shorts
```

## ESTRUTURA DO ROTEIRO

### Formato simples
```
Texto do segmento 1.

Texto do segmento 2.

Texto do segmento 3.
```

### Formato com tempo (SRT)
```
00:00:00,000 --> 00:00:05,000
Texto do segmento 1

00:00:05,000 --> 00:00:10,000
Texto do segmento 2
```

## DICAS DE COPYWRITING

### Para vídeos curtos (30-60s)
1. **Gancho**: Primeiros 3 segundos - problema ou curiosidade
2. **Desenvolvimento**: 2-3 argumentos principais
3. **CTA**: Último segmento - ação clara

### Estrutura recomendada
```
Problema → Consequência → Solução → Benefício → CTA
```

### Exemplo
```
Seu anúncio não está gerando resultados?

O problema pode ser a página onde o tráfego chega.

Uma landing page rápida e estratégica converte mais.

Mais conversões com menos investimento.

Solicite uma análise gratuita em fvs7.com.br
```

## COMENTÁRIOS AUTOMÁTICOS

### Status: PENDENTE - Autenticação Necessária
Para adicionar comentários via API, é necessário re-autenticar com o escopo `youtube.force-ssl`. O token atual não possui essa permissão.

**Solução**: Adicionar comentários manualmente via YouTube Studio ou re-autenticar com novos escopos quando possível.

### Regra: Comentário Pinned Automático
Ao publicar/agendar um vídeo, **SEMPRE** adicionar um comentário fixo com:
1. **Hook** → Pergunta ou afirmação que gera engajamento
2. **CTA** → Link para diagnóstico grátis
3. **Prova social** → Número de clientes ou resultados
4. **Emoji** → Chamar atenção visual

### Template de Comentário
```
🎯 Quer resultado assim na sua empresa?

👉 Acesse: fvs7.com.br/diagnostico-gratuito
📊 Diagnóstico gratuito em 15 minutos
💼 +150 empresas atendidas | 4.9/5 avaliação

#GoogleAds #MarketingDigital
```

### Limitação da API YouTube
- **NÃO É POSSÍVEL** fixar (pin) comentários via API v3
- Comentários são adicionados normais (sem pin)
- Para fixar, usar o YouTube Studio manualmente

### Comentário de Resposta (Opcional)
Quando alguém comentar algo relevante, responder com:
- Agradecimento
- Convite para diagnóstico
- Link do site

## THUMBNAILS AUTOMÁTICAS

### Visão Geral
A skill gera thumbnails profissionais (1280x720) automaticamente junto com os vídeos. Thumbnails aumentam o CTR (taxa de cliques) no YouTube.

### 3 Estilos de Thumbnail

| Estilo | Uso | Exemplo |
|--------|-----|---------|
| **nicho** | Advogados, Clínicas, Contadores, etc. | "Contadores: 3x Mais Leads" |
| **lista** | "3 Erros", "5 Dicas", listas | "3 Erros de Google Ads" |
| **depoimento** | Depoimentos, cases, antes/depois | "Depoimento: 50 Agendamentos" |

### Cores por Nicho

| Nicho | Cor de Destaque |
|-------|-----------------|
| Advogados | `#FFD700` (amarelo) |
| Clínicas | `#00d2d3` (ciano) |
| Contadores | `#54a0ff` (azul) |
| Fisioterapeutas | `#54a0ff` (azul) |
| Psicólogos | `#00d2d3` (ciano) |
| Imobiliárias | `#FFD700` (amarelo) |
| Esteticistas | `#ff6b6b` (rosa) |
| Negócios Locais | `#FFD700` (amarelo) |
| Marketing | `#e94560` (vermelho) |
| Landing Pages | `#00d2d3` (ciano) |
| Tracking | `#54a0ff` (azul) |

### Elementos Visuais

1. **Barra lateral** — Cor de destaque do nicho
2. **Forma de destaque** — Círculo, triângulo ou aspas
3. **Título grande** — Máximo 5 palavras, branco com sombra
4. **Número** — Quando aplicável, grande e colorido
5. **Nicho** — Subtítulo com cor de destaque
6. **Branding** — Logo FVS7 + "MARKETING DIGITAL"
7. **CTA** — Botão "VER AGORA"

### Regras de Design

- **Tamanho**: 1280x720 pixels (padrão YouTube)
- **Formato**: PNG
- **Legibilidade**: Texto legível em 360px (mobile)
- **Contraste**: Mínimo 4.5:1 (WCAG AA)
- **Fontes**: Sans-serif apenas (DejaVu, Liberation, Ubuntu)
- **Máximo texto**: 5 palavras no título

### Comandos

#### Gerar thumbnail isoladamente
```bash
cd ~/.config/opencode/skills/video-creator/scripts

# Estilo lista
python make_thumbnail.py \
  --titulo "3 Erros de Google Ads" \
  --nicho "marketing" \
  --tipo "lista"

# Estilo nicho com número
python make_thumbnail.py \
  --titulo "50 Agendamentos" \
  --nicho "clinicas" \
  --tipo "nicho" \
  --numero "50"

# Estilo depoimento
python make_thumbnail.py \
  --titulo "Depoimento Clínica" \
  --nicho "advogados" \
  --tipo "depoimento" \
  --output ~/Videos/thumbnails/custom.png
```

#### Parâmetros
| Parâmetro | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `--titulo` | Sim | Título do vídeo (máx 5 palavras) |
| `--nicho` | Sim | Nicho do vídeo |
| `--tipo` | Não | Estilo: nicho, lista, depoimento (padrão: lista) |
| `--numero` | Não | Número para destaque |
| `--output` | Não | Caminho de saída |

### Integração com Geração de Vídeo

Ao gerar um vídeo, a thumbnail é criada automaticamente:

```bash
# O make_video.py chama make_thumbnail.py automaticamente
cd ~/video-maker
python make_video.py \
  --file roteiro.txt \
  --audio \
  --search-images \
  --search-query "marketing digital" \
  --thumbnail \  # ← Adicionar este flag
  --output ~/Videos/video-maker/meu_video.mp4
```

### Saída Gerada
1. **Vídeo**: Arquivo .mp4
2. **Thumbnail**: Arquivo .png (1280x720)
3. **Metadados**: Título, descrição, hashtags

## SEO COM PALAVRAS-CHAVE

### Visão Geral
Otimizar títulos e descrições com palavras-chave de alto volume e intenção comercial para aumentar CTR e atrair leads qualificados.

### Regra de Ouro: Keyword no Início do Título

**OBRIGATÓRIO**: Colocar a keyword principal nos **primeiros 3 caracteres** do título.

| Posição | Prioridade | Exemplo |
|---------|------------|---------|
| Início (0-3 chars) | ⭐⭐⭐ | **Google Ads** + ... |
| Após dois-pontos | ⭐⭐ | Clínicas: **Landing Page** + ... |
| Meio do título | ⭐ | Evitar |
| Final do título | ❌ | Evitar |

### Banco de Palavras-Chave

**Localização**: `~/.config/opencode/skills/video-creator/keywords/banco_keywords.json`

**Estrutura por nicho**:
```json
{
  "nicho": {
    "keywords_principais": [
      {"keyword": "...", "volume": 720, "intencao": "comercial", "cpc": 4.50}
    ],
    "keywords_semanticas": ["...", "..."],
    "gatilhos": ["...", "..."]
  }
}
```

### Prioridade de Keywords

| Critério | Peso | Descrição |
|----------|------|-----------|
| Intenção comercial | 40% | Busca ativa por serviço/produto |
| Volume de busca | 30% | Demanda real no mercado |
| Relevância para nicho | 20% | Conexão com o público-alvo |
| CPC | 10% | Indicador de competitividade |

**Fórmula**: Prioridade = (Volume × Intenção × Relevância) ÷ CPC

### Template de Título Obrigatório

```
[KEYWORD PRINCIPAL]: [NÚMERO/RESULTADO] + [BENEFÍCIO]
```

### Exemplos por Nicho

| Nicho | Keyword | Título Otimizado |
|-------|---------|------------------|
| Clínicas | "landing page clínica" | **Landing Page** Clínica: 50 Agendamentos/Mês |
| Advogados | "marketing jurídico" | **Marketing Jurídico**: Como Advogados Captam Clientes |
| Contadores | "captação clientes" | **Captação de Clientes**: 3x Mais Leads PJ |
| Marketing | "google ads" | **Google Ads**: 3 Erros que Queimam Seu Dinheiro |
| LP | "landing page" | **Landing Page** que VENDE: O Segredo 95% Ignoram |

### Regras de Descrição

1. **Primeira linha** = Título + keyword principal
2. **Segunda linha** = Gancho ou dor do público
3. **Keywords semânticas** = 2-3 distribuídas naturalmente
4. **CTA** = Link com UTM
5. **Hashtags** = Máximo 5

### Keywords Semânticas por Nicho

| Nicho | Keywords Semânticas (usar 2-3) |
|-------|-------------------------------|
| Clínicas | agendamento, paciente, consulta, marketing médico, conversão |
| Advogados | clientes, escritório, advocacia, captação, ROI |
| Contadores | PJ, imposto, contador, faturamento, leads |
| Marketing | ROI, CPA, CTR, segmentação, orçamento, lance |
| Landing Pages | conversão, lead, formulário, CTA, UX, funil |

### Comandos

#### Sugerir keywords e título
```bash
cd ~/.config/opencode/skills/video-creator/scripts

# Sugerir para clínicas
python suggest_keywords.py --nicho "clinicas" --tema "agendamento"

# Sugerir para marketing
python suggest_keywords.py --nicho "marketing" --tema "google ads"

# Salvar resultado em JSON
python suggest_keywords.py --nicho "advogados" --tema "captação" --output ~/sugestao.json
```

#### Parâmetros
| Parâmetro | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `--nicho` | Sim | Nicho do vídeo |
| `--tema` | Sim | Tema principal do vídeo |
| `--output` | Não | Caminho para salvar JSON |
| `--json` | Não | Apenas retorna JSON |

### Validação de Título

Antes de publicar, verificar:

| Critério | OK | Erro |
|----------|-----|------|
| Keyword nos primeiros 3 chars | ✅ | ❌ |
| Máximo 50 caracteres | ✅ | ❌ |
| Número específico (quando possível) | ✅ | ❌ |
| Sem perguntas no início | ✅ | ❌ |
| Palavras de impacto | ✅ | ❌ |

### Validação de Descrição

| Critério | OK | Erro |
|----------|-----|------|
| Primeira linha = título | ✅ | ❌ |
| 2-3 keywords semânticas | ✅ | ❌ |
| Link com UTM | ✅ | ❌ |
| Máximo 5 hashtags | ✅ | ❌ |
| Sem \n duplicados | ✅ | ❌ |

## COMMON ISSUES

### Imagens irrelevantes
**Problema**: Pexels retorna imagens de mercado financeiro ou outros temas
**Solução**: USAR SOMENTE queries de marketing/digital/analytics (ver Regra 1)

### Narração com erros
**Problema**: Voz robótica ou sem expressividade
**Solução**: Ajustar rate/pitch no edge-tts ou usar voz diferente

### Vídeo sem identidade
**Problema**: Sem cores/fontes da marca
**Solução**: Usar `BRAND_TEXT` e `CTA_URL` definidos no script

### Solicitação de melhoria
**Problema**: Usuário pede para criar nova versão
**Solução**: CORRIGIR o vídeo existente, não criar v2, v3, etc. (ver Regra 3)

### Thumbnail não gera
**Problema**: Erro ao executar make_thumbnail.py
**Solução**: Verificar se Pillow está instalado: `pip install Pillow`

## ARQUIVOS RELACIONADOS

- `~/video-maker/make_video.py` - Script principal
- `~/video-maker/roteiros/` - Roteiros salvos
- `~/Videos/video-maker/` - Vídeos gerados
- `~/Videos/thumbnails/` - Thumbnails geradas
- `~/.config/opencode/skills/video-creator/scripts/make_thumbnail.py` - Script de thumbnails
- `~/.config/opencode/skills/video-creator/brand-guidelines.md` - Identidade visual

## RASTREAMENTO GA4 - UTMs

### Estrutura de UTM para YouTube Shorts
Todo link na descrição DEVE conter UTMs para rastreamento no GA4.

**URL Base**: `fvs7.com.br/diagnostico-gratuito`

**Parâmetros UTM**:
| UTM | Valor | Descrição |
|-----|-------|-----------|
| `utm_source` | `youtube` | Fonte do tráfego |
| `utm_medium` | `shorts` | Tipo de conteúdo |
| `utm_campaign` | `{VIDEO_ID}` | ID do vídeo no YouTube |
| `utm_content` | `{NICHE}` | Nicho/tema do vídeo |

### Nomes de Nicho para utm_content
| Nicho | Valor UTM |
|-------|-----------|
| Clínicas de estética | `clinicas` |
| Advogados | `advogados` |
| Contadores | `contadores` |
| Fisioterapeutas | `fisioterapeutas` |
| Psicólogos | `psicologos` |
| Imobiliárias | `imobiliarias` |
| Esteticistas | `esteticistas` |
| Negócios Locais | `negocios_locais` |
| Landing Pages/CRO | `landing_pages` |
| Tracking/GA4 | `tracking` |
| Marketing Digital | `marketing` |

### Exemplo de Link com UTM
```
https://fvs7.com.br/diagnostico-gratuito?utm_source=youtube&utm_medium=shorts&utm_campaign=ds8O7QfE6EA&utm_content=clinicas
```

### Como Visualizar no GA4
1. **Relatórios** → **Aquisição** → **Tráfego por sessão**
2. Filtrar por: `utm_source=youtube`
3. Ver por: `utm_campaign` (qual vídeo) e `utm_content` (qual nicho)
4. **Relatórios** → **Conversões** → Filtrar por source=youtube

### Métricas Importantes no GA4
| Métrica | O que mostra |
|---------|--------------|
| Sessões por campaña | Qual vídeo trouxe mais tráfego |
| Taxa de conversão por nicho | Qual nicho converte melhor |
| Receita por source | ROI do YouTube como canal |
| Tempo na página | Qualidade do tráfego |
