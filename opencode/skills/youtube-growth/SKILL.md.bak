---
name: youtube-growth
description: Gerenciador e centro de inteligência para canal do YouTube Shorts. Consome output da video-creator para publicar, agendar, analisar e otimizar vídeos.
---

# YOUTUBE GROWTH MANAGER

## OBJETIVO

Transformar o OpenCode em um gerenciador e centro de inteligência para um canal do YouTube Shorts, consumindo o output produzido pela skill `video-creator`.

Este skill NÃO cria vídeos, roteiros, títulos ou descrições. Ele consome o output da `video-creator` e fornece funcionalidades para:

- Upload de vídeos para YouTube
- Agendamento de publicação (usando agendamento nativo do YouTube)
- Gerenciamento da agenda de publicações
- Análise de desempenho (YouTube Analytics)
- Auditoria SEO
- Pesquisa de palavras-chave
- Análise de concorrentes
- Estratégia de crescimento
- Histórico local de publicações

## ARQUITETURA

```text
video-creator
       │
       ├── video.mp4
       │
       └── video.txt
              │
              ▼
       youtube-growth
              │
       ├── Upload
       ├── SEO audit
       ├── Agendamento
       ├── Publicação
       ├── Gerenciamento
       ├── Analytics
       ├── Keyword research
       ├── Concorrentes
       └── Growth strategy
```

## LOCALIZAÇÃO DOS ARQUIVOS

A skill `video-creator` salva arquivos em:
- Vídeo: `/home/fvitorio/Videos/video-maker/{name}.mp4`
- Metadados: `/home/fvitorio/Videos/video-maker/{name}.txt`

Esta skill procura por esses pares de arquivos para processar.

## FORMATO DO ARQUIVO .TXT

O arquivo .txt gerado pela video-creator possui esta estrutura:

```
════════════════════════════════════════════════════════════════
TÍTULO (para YouTube Shorts / Reels / TikTok)
════════════════════════════════════════════════════════════════

Google Ads + Landing Page: A Fórmula para Mais Vendas

════════════════════════════════════════════════════════════════
DESCRIÇÃO (copie e cole)
════════════════════════════════════════════════════════════════

Google Ads + Landing Page: A Fórmula para Mais Vendas

🎯 Quer resultados reais com Google Ads e Landing Pages?

A FVS7 Growth é especializada em transformar tráfego pago em leads e clientes para seu negócio.

✅ Google Ads gerenciado por especialistas
✅ Landing pages rápidas e otimizadas para conversão
✅ Tracking completo: WhatsApp, formulários e GA4
✅ Otimização semanal com base em dados reais

📊 Resultados comprovados:
• +150 projetos entregues
• 4.9/5 avaliação dos clientes
• Nota 100% no GTmetrix

🔥 Seu anúncio pode gerar o clique. Sua página precisa gerar o resultado.

👉 Acesse agora: https://fvs7.com.br/

📞 Fale conosco: https://fvs7.com.br/atendimento/

#GoogleAds #MarketingDigital #TráfegoPago #LandingPage #GestãoDeTráfego #Leads #Conversão #SEO #FVS7

════════════════════════════════════════════════════════════════
HASHTAGS (para usar nos comentários ou descrição)
════════════════════════════════════════════════════════════════

#GoogleAds #MarketingDigital #TráfegoPago #LandingPage #Marketing #FVS7

════════════════════════════════════════════════════════════════
CHECKLIST DE PUBLICAÇÃO
════════════════════════════════════════════════════════════════
...
```

O parser desta skill extrairá:
- title: conteúdo da seção "TÍTULO"
- description: conteúdo da seção "DESCRIÇÃO" 
- hashtags: conteúdo da seção "HASHTAGS"

Textos marcadores como "TÍTULO", "DESCRIÇÃO", etc. NÃO serão incluídos no conteúdo enviado ao YouTube.

## REQUISITOS PRÉVIOS

Antes de usar esta skill, é necessário:

1. Configurar um projeto no Google Cloud Console
2. Ativar a YouTube Data API v3
3. Configurar credenciais OAuth 2.0
4. Autorizar o acesso ao canal do YouTube

As credenciais serão armazenadas em:
`/home/fvitorio/.config/opencode/credentials/youtube-token.json`

## ESCOPES NECESSÁRIOS

Esta skill solicita os seguintes escopos mínimos:
- `https://www.googleapis.com/auth/youtube.upload` (para upload e gerenciamento de vídeos)
- `https://www.googleapis.com/auth/youtube.readonly` (para leitura de dados do canal)
- `https://www.googleapis.com/auth/yt-analytics.readonly` (para acesso ao YouTube Analytics)
- `https://www.googleapis.com/auth/youtubepartner` (para acesso a relatórios detalhados, se disponível)

## CONFIGURAÇÃO PADRÃO

A skill usa a seguinte configuração padrão (pode ser sobrescrita):

```yaml
channel:
  language: "pt-BR"
  country: "BR"
  timezone: "America/Sao_Paulo"

publishing:
  default_visibility: "private"
  require_confirmation_for_public: true

seo:
  audit_before_publish: true
  auto_optimize: false

analytics:
  default_period_days: 30
```

## SEGURANÇA

Esta skill separa operações em:
- READ: leitura de dados (canal, vídeos, analytics, keywords)
- ANALYZE: análise (relatórios, SEO, growth audit, concorrentes)
- WRITE: modificação de metadados (título, descrição, playlists)
- PUBLISH: ações públicas (upload, publicação, agendamento, cancelamento)

Ações potencialmente destrutivas ou públicas exigem confirmação quando configurado.

## LOGS

Operações importantes são registradas com o prefixo `[YouTube]`.

Exemplos:
- `[YouTube] Authentication successful`
- `[YouTube] Found video`
- `[YouTube] Metadata parsed`
- `[YouTube] Upload started`
- `[YouTube] Upload completed`
- `[YouTube] Video ID: abc123`
- `[YouTube] Scheduled: 2026-09-22 06:00 America/Sao_Paulo`

Em caso de erro:
- `[YouTube] Upload failed`
- `Reason: ...`
- `Action: ...`

Nunca afirmar que uma publicação ocorreu sem confirmar o estado real no YouTube.

## IDMPOTÊNCIA

Antes de enviar um vídeo, a skill verifica:
- Histórico local existente
- Se existe video_id associado
- Estado atual no YouTube
- Evita uploads duplicados

Se uma operação falhar depois do upload, primeiro consulta o YouTube antes de tentar novamente.

## HISTÓRICO LOCAL

Mantém um histórico local em:
`/home/fvitorio/.config/opencode/skills/youtube-growth/history.json`

Para cada vídeo registra:
- video_id
- video_file
- metadata_file
- title
- description
- hashtags
- youtube_url
- uploaded_at
- scheduled_at
- published_at
- status
- topic (opcional)
- keywords (opcional)
- duration (opcional)
- thumbnail (opcional)

O YouTube continua sendo a fonte de verdade sobre o estado atual. O banco local serve para histórico, análise e correlação.