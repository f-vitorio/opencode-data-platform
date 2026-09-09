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
  --output ~/Videos/video-maker/nome_video.mp4

# Com áudio customizado
python make_video.py \
  --file roteiro.txt \
  --audio caminho/audio.mp3 \
  --search-images \
  --search-query "QUERY" \
  --output output.mp4
```

### Parâmetros importantes
- `--file`: Arquivo de roteiro (.txt)
- `--audio`: Ativa narração ElevenLabs (sem argumento) ou usa áudio customizado
- `--search-images`: Busca imagens no Pexels
- `--search-query`: Query de busca (IMPORTANTE: usar query específica)
- `--output`: Caminho de saída

### Saída Gerada
1. **Vídeo**: Arquivo .mp4 com identidade visual FVS7
2. **Metadados**: Arquivo .txt com título SEO, descrição e hashtags
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

### Títulos Otimizados para YouTube
- Máximo 100 caracteres
- Palavra-chave principal no início
- Formato: "Como [BENEFÍCIO] com [SOLUÇÃO]"
- Exemplos:
  - "Como Lotar a Agenda da Sua Clínica com Google Ads"
  - "Google Ads para Advogados: Estratégia que Funciona"
  - "Landing Page: Como Converter Mais Visitantes em Leads"

### Descrição Persuasiva
- Hook na primeira linha
- Benefícios com emojis
- Prova social (+150 projetos, 4.9/5 avaliação)
- CTA claro com link
- Hashtags relevantes

### Hashtags Recomendadas por Nicho
- **Clínicas**: #GoogleAds #Clínica #Estética #Pacientes #Agendamento
- **Advogados**: #Advogado #MarketingJurídico #ClientesPremium
- **Contadores**: #Contador #Contabilidade #LeadsB2B
- **Marketing**: #MarketingDigital #TráfegoPago #LandingPage

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

## ARQUIVOS RELACIONADOS

- `~/video-maker/make_video.py` - Script principal
- `~/video-maker/roteiros/` - Roteiros salvos
- `~/Videos/video-maker/` - Vídeos gerados
- `~/.config/opencode/skills/video-creator/brand-guidelines.md` - Identidade visual
