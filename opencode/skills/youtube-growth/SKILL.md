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
- Pacote de publicação manual no TikTok (legenda pronta, sem API)

## REGRA INVIOLÁVEL DE SEO (TÍTULO E DESCRIÇÃO)

**Todo título e toda descrição COMEÇAM com a palavra-chave correta, por extenso.
Nenhuma abreviação é aceita. Esta regra não sofre exceção.**

1. **Título** começa com a keyword principal (banco da `video-creator`) ou o termo do nicho
   (Clínicas, Psicólogos, Contadores, Google Ads, Landing Page, Tráfego Pago...).
2. **Primeira linha da descrição** começa com a mesma keyword.
3. **Nenhuma abreviação** em título ou descrição:

   | Abreviação proibida | Escrever por extenso |
   |---|---|
   | LP, LPs | landing page, landing pages |
   | MKT | marketing |
   | GA | Google Ads / Google Analytics |
   | CONV | conversão |
   | CAP | captação |
   | PÁG | página |
   | CLI | cliente |

4. A regra vale para **upload, agendamento, atualização de metadados e tiktok-package**:
   se falhar, a skill **bloqueia** e não toca na API nem gera arquivo. Nunca publique
   contornando o bloqueio.

Exemplos:

| Errado | Correto |
|---|---|
| `95% das LPs Erram Isso: 6x Mais Conversões` | `Landing Page: 95% Erram Isso, Perdem 6x Conversões` |
| `Sua LP não vende?` | `Landing Page não vende?` |
| `MKT: 3 Erros que Queimam Orçamento` | `Marketing Digital: 3 Erros que Queimam Orçamento` |

Auditoria (READ/ANALYZE — não modifica nada; `0` = PASS, `1` = FAIL):

```bash
python3 ~/.config/opencode/skills/youtube-growth/youtube_growth.py seo-audit --title "Título" --description "Primeira linha"
python3 ~/.config/opencode/skills/youtube-growth/youtube_growth.py seo-audit ~/Videos/video-maker/arquivo.txt
python3 ~/.config/opencode/skills/youtube-growth/youtube_growth.py seo-audit <video_id_ou_nome>
python3 ~/.config/opencode/skills/youtube-growth/youtube_growth.py seo-audit --history   # audita todo o histórico local
```

O mesmo bloqueio roda automaticamente dentro de `upload`, `schedule` e `update_metadata`.
Se o `.txt` da video-creator estiver fora do padrão, corrija o `.txt` antes de publicar.

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
       ├── Pacote TikTok (legenda pronta, publicação manual)
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

👉 Diagnóstico grátis: https://fvs7.com.br/diagnostico-gratuito?utm_source=youtube&utm_medium=shorts&utm_campaign=VIDEO_ID&utm_content=niche

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

Escopos **realmente concedidos** pelo token salvo
(`~/.config/opencode/credentials/youtube-token.json` → chave `scopes`):

- `https://www.googleapis.com/auth/youtube` — upload e edição de vídeos/comentários
- `https://www.googleapis.com/auth/youtube.force-ssl` — **necessário para inserir comentários**
- `https://www.googleapis.com/auth/youtube.readonly` — leitura do canal
- `https://www.googleapis.com/auth/yt-analytics.readonly` — retenção no `check_24h.py`

Se `scopes` não contiver `youtube.force-ssl`, o comando `comment` falha com
`403 insufficientPermissions` — nesse caso reautorizar a skill.

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
  keyword_first: true          # título e 1ª linha da descrição começam com a keyword
  forbid_abbreviations: true   # LP → landing page, MKT → marketing, GA → Google Ads
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
- status (`uploaded` | `scheduled` | `published` | `deleted` — `deleted` = o video_id não existe mais no canal)
- comment_id / commented_at (comentário de CTA, se já criado)
- tiktok: `{status, caption_file, copy_url, bio_url, buffer_post_id, ...}` (opcional)
- topic (opcional)
- keywords (opcional)
- duration (opcional)
- thumbnail (opcional)

O YouTube continua sendo a fonte de verdade sobre o estado atual. O banco local serve para histórico, análise e correlação.

## CHECK 6H/24H (pós-publicação)

Após cada publicação, rodar para monitorar views/likes/comentários/retenção:

```bash
python3 ~/.config/opencode/skills/youtube-growth/check_24h.py
python3 ~/.config/opencode/skills/youtube-growth/check_24h.py --window 6
```

- Janelas padrão: 6h e 24h (últimas 48h de `published_at` BRT).
- Gate de retenção: `averageViewPercentage > 60%` = PASS.
- FAIL → analisar curva no Studio antes de escalar / reativar guardados.
- Pendências manuais: `PENDENTES.md` (mesmo diretório).
- Também imprime a seção **COMENTÁRIOS PENDENTES**: vídeos **públicos** sem
  comentário de CTA (somente leitura).

## COMENTÁRIO COM CTA (link clicável no vídeo)

Nenhum link do YouTube Shorts é clicável de verdade (descrição de Shorts abre
pior que a de vídeo longo). Quem assiste e quer agir, olha os **comentários**.
Então cada vídeo público leva **um comentário com link rastreável**.

- Texto: `build_pinned_comment()` — template da video-creator, ≤997 chars
- URL: `generate_utm_url(video_id, niche)` → `utm_source=youtube&utm_medium=shorts&utm_campaign=<video_id>`
- Idempotente: se `comment_id` já existe no histórico, não duplica
- A **API não fixa (pin)** comentário — fixar é manual no Studio

```bash
# um vídeo
python3 ~/.config/opencode/skills/youtube-growth/youtube_growth.py \
  --yes comment <nome_ou_video_id>

# varredura dos pendentes
python3 ~/.config/opencode/skills/youtube-growth/check_24h.py
```

Quando o comentário é criado sozinho:

| Momento | Comportamento |
|---|---|
| `upload` | não comenta — o vídeo sai `private` e o YouTube recusa comentário |
| `publish-now` | **comenta automaticamente** logo após virar `public` |
| `schedule-existing` | YouTube publica sozinho no `publishAt` → sem hook; usar `comment` depois |
| `check_24h.py` | só **lista** os pendentes (read-only) |

## TIKTOK (PACOTE SEMI-MANUAL)

A publicação no TikTok é **manual** — não existe API nem automação de navegador nesta
skill. O que existe é um pacote pronto para você colar no app/site.

### Fluxo

```bash
# 1. Gera a legenda pronta (bloqueia se falhar a regra de SEO)
python3 ~/.config/opencode/skills/youtube-growth/youtube_growth.py tiktok-package <nome_do_video>

# 2. Conferir pendentes
python3 ~/.config/opencode/skills/youtube-growth/youtube_growth.py tiktok-list

# 3. Depois de publicar manualmente no TikTok, registrar
python3 ~/.config/opencode/skills/youtube-growth/youtube_growth.py tiktok-published <nome_do_video>
```

### O que `tiktok-package` faz

- Fonte da legenda: **`history.json`** (descrição reescrita pela Ação 5 do
  `PENDENTES.md`); só cai no `.txt` se não houver entrada no histórico
- **Remove toda URL `fvs7.com.br`** da descrição — o TikTok não formata URL em
  legenda nem em comentário, então ali é texto morto
- Remove linhas órfãs de CTA que sobrariam depois da remoção
- Monta a legenda: **keyword na 1ª linha**, depois texto, **CTA duplo**
  (`🔗 Diagnóstico grátis — link na bio` + `🌐 Copie e cole: <utm>`) e hashtags
  no fim, corte em **2200 caracteres** (limite do TikTok) preservando o início
  **e** reservando CTA + hashtags na cauda
- Roda `seo_audit` antes de tudo: **falhou = nenhum arquivo gerado** (bloqueio total)
- Escreve `/home/fvitorio/Videos/video-maker/{nome}.tiktok.txt`
- Tenta copiar a legenda para a área de transferência (`wl-copy`/`xclip`/`xsel`)
- Registra no histórico: `tiktok: {status, caption_file, caption_chars,
  copy_url, bio_url, prepared_at}` — **preservando** `buffer_post_id` e
  `status: scheduled|published` já existentes (um pacote manual não cancela
  um agendamento do Buffer)
- Imprime as duas URLs: a da **bio** (a única clicável) e a de **cópia manual**

### As duas URLs do TikTok

| URL | Onde entra | UTM |
|---|---|---|
| `TIKTOK_BIO_URL` = `fvs7.com.br/diagnostico-gratuito?...&utm_campaign=perfil&utm_content=bio` | bio do perfil (**única clicável**) | `tiktok / social / perfil / bio` |
| `tiktok_utm_url(stem)` = mesma landing `...&utm_medium=shorts&utm_campaign=tiktok&utm_content=<stem>` | linha "Copie e cole" da legenda | `tiktok / shorts / tiktok / <stem>` |

O GA4 traz a distribuição: `bio` = cliques no link do perfil,
`<stem>` = quantas pessoas copiaram e colaram o link manualmente.

### Conferir a bio (manual)

A constante `TIKTOK_BIO_URL` está no topo de `youtube_growth.py`. Ela precisa
estar **exatamente** na bio do TikTok — é o único clique orgânico que a
plataforma entrega.

### Comandos

| Comando | Tipo | O que faz |
|---|---|---|
| `tiktok-package <nome>` | local | Gera `.tiktok.txt` + registra `prepared` |
| `tiktok-list` | READ | Lista pacotes e status |
| `tiktok-published <nome>` | local | Marca `status: published` + timestamp |

### Regras

- Nenhuma desses comandos publica nada no TikTok. Nunca afirmar publicação sem
  `tiktok-published` + confirmação visual no perfil.
- A legenda segue a mesma regra inviolável de SEO do YouTube.
- O gate de duração de 30s é do YouTube Shorts e **não** se aplica ao TikTok.
- O campo `tiktok` é opcional no histórico e não interfere no YouTube.
- **Nunca** prometer "clique no link" num vídeo do TikTok: o link da legenda não
  é clicável. O caminho é bio → diagnóstico, ou cópia manual.

## TIKTOK + BUFFER (AGENDAMENTO AUTOMÁTICO)

Além do pacote manual, é possível **agendar a publicação automática** no TikTok
pelo Buffer (GraphQL API). Nesse fluxo quem publica é o Buffer, não você.

### Fluxo

```bash
# Agenda publicação automática (horário em linguagem natural, fuso America/Sao_Paulo)
python3 ~/.config/opencode/skills/youtube-growth/youtube_growth.py \
  --yes tiktok-buffer <nome_do_video> --when "amanhã às 19h"

# Ver pendentes/agendados
python3 ~/.config/opencode/skills/youtube-growth/youtube_growth.py tiktok-list

# Cancela o agendamento no Buffer
python3 ~/.config/opencode/skills/youtube-growth/youtube_growth.py \
  --yes tiktok-buffer-cancel <nome_do_video>

# Reabastece a fila (publica 1/dia até o limite do plano; rode 1x ao dia)
python3 ~/.config/opencode/skills/youtube-growth/youtube_growth.py \
  --yes tiktok-buffer-fill
python3 ~/.config/opencode/skills/youtube-growth/youtube_growth.py \
  --yes tiktok-buffer-fill --limit 3 --hour 19

# Dry-run: mostra quas legendas agendadas estão desatualizadas
python3 ~/.config/opencode/skills/youtube-growth/youtube_growth.py \
  tiktok-caption-sync

# Aplica (editPost → só o texto muda; horário e vídeo ficam)
python3 ~/.config/opencode/skills/youtube-growth/youtube_growth.py \
  --yes tiktok-caption-sync
```

### `tiktok-caption-sync` (legenda dos posts já agendados)

O Buffer congela o texto no momento do `createPost`. Quando a legenda muda
depois (CTA de bio, descrição reescrita), os posts já na fila continuam com
o texto velho. Este comando:

1. Compara `history.json` → legenda regenerada com o `text` atual do Buffer
2. Roda o mesmo `seo_audit` — bloqueado = não envia
3. Diferente → `editPost(input:{id, text})`; igual → ignora
4. Post que sumiu da fila (já publicou / cancelou) → reporta, não erra
5. Regrava `caption_chars` + `caption_synced_at` no histórico

**Dry-run por padrão.** `--yes` é que altera.

### O que `tiktok-buffer` faz

1. Lê `{nome}.mp4` / `{nome}.txt` e monta a legenda (keyword na 1ª linha, ≤2200 chars)
2. **Bloqueio de SEO** — falhou = não envia nada
3. **Cloudinary** — sobe o vídeo e valida que a URL é pública (HTTPS, sem login)
4. **Buffer `createPost`** — canal TikTok, `schedulingType: automatic`,
   `mode: customScheduled`, `dueAt` em UTC
5. Registra no histórico: `tiktok: {status: "scheduled", buffer_post_id, video_url, scheduled_at}`

### Requisitos

- `~/.config/opencode/credentials/cloudinary.json` — `cloud_name`, `api_key`, `api_secret`
- `~/.config/opencode/credentials/buffer.json` — `token`, `organization_id`,
  `tiktok_channel_id`, `scheduled_cap` (limite de posts agendados do plano, hoje 10)
- Canal TikTok conectado no Buffer (`publish.buffer.com`)
- Vídeo em URL pública estável até o horário da publicação (o Buffer baixa na hora
  de publicar — não usar link que expira)

### `tiktok-buffer-fill` (fila com limite de plano)

O plano free do Buffer aceita **no máximo 10 posts agendados ao mesmo tempo**.
O fill contorna isso com uma fila rolante:

1. Lista elegíveis: `status: published` **ou** `scheduled` no histórico (ou seja,
   todo vídeo gerado que está no YouTube) + `.mp4`/`.txt` locais +
   sem `tiktok.status` scheduled/published
2. Ordem: publicados primeiro (por `uploaded_at`), depois os programados no
   YouTube (por `scheduled_at`) — o TikTok acompanha a mesma sequência
3. Conta os agendados no canal; vaga = `scheduled_cap − agendados`
4. Preenche as vagas nos próximos slots diários às 19h (America/Sao_Paulo),
   depois do último post da fila
5. Falha em um vídeo não derruba os demais (relatório ao final)

Rode **1x ao dia** (de manhã) — a cada post publicado, abre vaga para o próximo.
Comportamento idempotente: fila cheia = "nada a fazer".

**Cron ativo:** `7 9 * * *` roda o fill diariamente e escreve em
`tiktok_fill.log` (mesmo diretório). Backup do crontab antes da inclusão em
`/tmp/opencode/crontab.bak-*`.

### Regras e limites

- Idempotência: se já existe `status: scheduled` com `buffer_post_id`, bloqueia
  (use `tiktok-buffer-cancel` antes ou `--force`)
- Horário no passado = recusa
- A API aceita `automatic` para TikTok, mas **conta pessoal** pode receber só
  lembrete no app — confirme no Buffer antes do horário e trate
  `status: sent` como fonte de verdade
- Nunca afirmar publicação sem confirmar no Buffer/TikTok
- `tiktok-package` continua válido para publicação 100% manual

