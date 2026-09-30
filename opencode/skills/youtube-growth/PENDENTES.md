# PENDENTES — YouTube Shorts FVS7

Atualizado: 2026-09-29 16:45 BRT

## Plano de 5 ações (29/09/2026) — status

| # | Ação | Status |
|---|------|--------|
| 1 | Sync `history.json` ↔ YouTube | [x] concluída |
| 2 | Rechecks agendados (`pending_checks.json`) | [x] concluída |
| 3 | Gate de duração ≤30s em produção nova | [x] concluída |
| 4 | Re-up `deeDrwxpI3c` (esteticistas) | [ ] **CANCELADA (29/09)** — ver abaixo |
| 5 | Reescrita de valor das descrições | [x] concluída |

### 1 — Sync (29/09)
- [x] Backup `history.json.bak-20260929-160117-pre-sync`; 6 correções
      `scheduled → published`: `XwoKf6_ZeqY`, `ux6pZyLwHhc`, `CM3kMn2fLMo`,
      `WVPyhmqFNkg`, `r-ZIHnejd7w`, `xclcaUY3-W0`.
- [x] `sync_history.py` criado (dry-run default, `--apply`, `--backup`); idempotente.
- [x] `check_24h.py` reescrito: elegíveis via API (uploads playlist + `videos.list`),
      views de `statistics` (ao vivo), retenção Analytics com `NA` no lag, guarda de
      página repetida na paginação.
- Estado final: **published 31 / scheduled 67 / deleted 2** (100 entries).

### 2 — Rechecks (29/09)
- [x] `pending_checks.json` criado (arquivo separado: `history.json` é iterado como
      `{stem: dict}` por ~20 trechos — uma chave de lista lá quebraria os loops).
- [x] `check_24h.py` agora imprime a seção `RECHECKS VENCIDOS` com views ao vivo,
      limite (`threshold`) e acima/abaixo.
- [x] 4 entradas: `deeDrwxpI3c` (vencido, v=1 → dispara Ação 4), `XwoKf6_ZeqY` (30/09),
      `xclcaUY3-W0` (30/09), gate de retenção (03/10).

### 3 — Gate ≤30s (29/09)
- [x] `youtube_growth.py`: `probe_duration_seconds()` (ffprobe) + `MAX_SHORT_DURATION_S=30`
      bloqueando `upload_video` antes da chamada de insert (`:506`). Flag `--force`
      em `upload` e `schedule` como exceção documentada.
- [x] Testado nos dois caminhos: 84s → bloqueado sem upload; 23,1s → PASS até o insert.
- [x] `video-creator`: `prompts/generate-script.md` (duração 20-30s, orçamento 65-75
      palavras, segmentos 4-6, exemplo reescrito para 64 palavras) e `SKILL.md`
      (seção GATE DE DURAÇÃO, "Para vídeos curtos (≤30s)", exemplo de saída).
- Evidência: 10 dias/22 vídeos → ≤26s = 34 views | 51–85s = 11 views.

### 5 — Descrições (29/09)
- [x] `rewrite_value_descriptions.py`: **64/64 aplicadas, 0 falhas**. 3 ignoradas por
      `replaced_by` (`video_auditoria_gratis`, `video_fisioterapeutas`, `video_psicologos`).
- [x] Removido em todas: `✅ Ads especialistas | …` e `📊 +150 projetos | 4.9/5 | 100% GTmetrix`.
      Título, CTA com UTM e hashtags preservados; `publishAt` intacto (67 agendamentos).
- [x] Copy manual dos 3 `hook_video_*` preservada (prioridade sobre o roteiro).
- [x] Validação: `seo-audit --history` → **0/98 fora do padrão**; `.txt` locais → 0 com bloco.
- Backup: `history.json.bak-20260929-163850-pre-acao5`.

### 4 — Re-up estética: CANCELADA (29/09, decisão do gestor)
- [x] Recheck de `deeDrwxpI3c` concluído: **v=1** (limite 5) → abaixo. Fechado em
      `pending_checks.json` com o `outcome`.
- [ ] **Não re-upar.** Motivo: **ambos os assets ≤30s têm o mesmo hook queimado** —
      `"Quero mais clientes para seu estúdio de estética?"` (`esteticistas.mp4` 23,1s e
      `test_esteticista.mp4` 23,1s). É **estruturalmente o exemplo de hook inválido**
      da própria skill (`video-creator/prompts/generate-script.md:58`): pergunta vaga,
      sem número, sem dor. Trocar título/descrição **não mexe nos 3s iniciais**, que é
      onde o Short é decidido — um re-up geraria a conclusão falsa de "ângulo novo não
      funcionou".
- [x] Teste do nicho estética fica com os **3 já agendados** + `B0QaHuWQLOs`:
  - `outubro_20_estetica_agenda_lotada` → `TI-iFAZVk_E` — "Agenda com buraco? 3 erros de segmentação"
  - `outubro_36_estetica_procedimentos` → `E0vGMqpYlAs` — "Procedimento certo no anúncio = agenda lotada"
  - `outubro_57_estetica_black_friday` → `pwXnJ6eRipc` — "Black Friday: lotar agenda sem perder margem"
  - `hook_video_esteticistas` → `B0QaHuWQLOs` (51,6s; hook "vagas se perdem" ✓, mas visual
    de gráfico corporativo genérico — fora do nicho. Mantido agendado por decisão.)
- [ ] Se os agendados também zerarem → **re-render com hook correto** (número+dor, ≤8
      palavras, ≤30s, imagens de estética real), não outro re-up.

**Falso positivo de duração (29/09):** o corte por duração é confundido por idade dos
vídeos. Publicados ≤30s: n=7, média 101 / **mediana 25**; ≥51s: n=22, média 505 /
mediana 12 (as médias são puxadas pelos vídeos de fev/2026). O gate de 30s da Ação 3
segue válido para produção nova, mas a evidência real é a **mediana**, não a média.

## Manual (Studio — inacessível via API)
- [ ] **#8** Impressions/CTR (API não expõe `impressions`).
      **Prioridade: `XwoKf6_ZeqY` = 0 views em 28h** — anômalo (outros recentes: 7–16).
      Se `impressions = 0` → é distribuição/restrição, não ângulo. Antes de qualquer re-up.
- [ ] **#9** Saúde do canal / audience retention curve por vídeo no Studio.
- [ ] **#11** Confirmar `defaultAudioLanguage=en-US` vs `defaultLanguage=pt-PT`
      nos vídeos — hipótese de afetar distribuição, não confirmada.
- [ ] Pin manual do comentário CTA (API não suporta pin).

## Executado em 2026-09-24
- [x] **P0 #1** — 32 vídeos agendados 18:00 BRT (21:00Z), 1/dia, 24/09–31/10.
- [x] **P0 #2** — 32 títulos reescritos (padrão número+dor+especificidade), API + history + .txt locais sincronizados. 0 mismatch.
- [x] **P0 #3** — 32 thumbnails geradas (1280×720) e enviadas via `thumbnails.set`. 32/32 com maxres.
- [x] **P0 #4** — `check_24h.py` criado (janelas 6h/24h, gate retenção >60%) e documentado no SKILL.md.
- [x] **P1 #5a** — Hooks auditados nos 5 roteiros 24–28/09; 2 reescritos (`auditoria_gratis`, `negocios_locais`) para ≤8 palavras + número. Backup em `roteiros/.bak-20260924/`.
- [x] **P1 #6** — Comentário CTA postado em 12 vídeos publicados recentes (12/12).

## Leva 12:00 BRT — CONCLUÍDA (26/09/2026)
- [x] **31 de 32 agendados** (15:00Z = 12:00 BRT): `video_negocios_locais` em 27/09 e
      30 vídeos de 02/10 a 31/10. Script corrigido (`schedule_pending_12h.py`): datas por
      horário livre a partir de 27/09 (o índice fixo antigo tentava agendar 25/09 — passado —
      e colidia com 30/09 e 01/10).
- [x] **`video_auditoria_gratis` (`qNh9Rt7uqIY`) agendado manualmente no Studio**
      (26/09): **01/11/2026 12:00 BRT**. A API continua recusando `400 invalidPublishAt`
      para alterar esse vídeo (só o Studio consegue), por isso a tarefa é manual.
      `history.json` sincronizado: `scheduled` / `2026-11-01T15:00:00`.
- [x] Verificado via API: 72 agendamentos, 0 colisões, 0 divergência com `history.json`.
- [x] `calendario-outubro-2026.md` atualizado (2/dia, 72 agendamentos).
- [x] SEO audit dos agendados: 0 fora do padrão (gate de agendamento ativo em `schedule_existing_publish`).

## Executado em 2026-09-24 (re-render autorizado)
- [x] **#5 real** Re-render dos 2 hooks corrigidos:
  - `hook_video_auditoria_gratis` → **Z7Mz2n8vchk** (25/09 21:00Z); old `nEXalGxclK0` deletado.
  - `hook_video_negocios_locais` → **xclcaUY3-W0** (28/09 21:00Z); old `m_2Cqp8PqiA` deletado.
  - Roteiros: `.bak-20260924/`; mp4s novos em `video-maker/rehook-done/`; thumbs reapontadas.

## Comandos úteis
```bash
python3 ~/.config/opencode/skills/youtube-growth/check_24h.py     # rechecks + check 6h/24h
python3 ~/.config/opencode/skills/youtube-growth/sync_history.py  # sync (dry-run)
python3 ~/.config/opencode/skills/youtube-growth/rewrite_value_descriptions.py --examples 2
```
