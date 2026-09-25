# PENDENTES — YouTube Shorts FVS7

Atualizado: 2026-09-24 10:05 BRT

## Leva 12:00 BRT (38 guardados → 1/dia a partir de 25/09)
- [x] 6 agendados com sucesso: 25/09, 26/09, 28/09, 29/09, 30/09, 01/10 (15:00Z = 12:00 BRT)
- [ ] **32 restantes** — cota da YouTube Data API estourou no meio. Retomar com:
  ```bash
  python3 ~/.config/opencode/skills/youtube-growth/schedule_pending_12h.py
  ```
  Reset da cota: ~04:00 BRT (meia-noite Pacifico). Prazo crítico: antes de 27/09 (primeiro pendente).
- [ ] Após retomada: verificar via API que os 38 têm `publishAt` = 15:00Z (idempotência).
- [ ] Atualizar `calendario-outubro-2026.md` com a leva das 12:00.

## Executado em 2026-09-24
- [x] **P0 #1** — 32 vídeos agendados 18:00 BRT (21:00Z), 1/dia, 24/09–31/10.
- [x] **P0 #2** — 32 títulos reescritos (padrão número+dor+especificidade), API + history + .txt locais sincronizados. 0 mismatch.
- [x] **P0 #3** — 32 thumbnails geradas (1280×720) e enviadas via `thumbnails.set`. 32/32 com maxres.
- [x] **P0 #4** — `check_24h.py` criado (janelas 6h/24h, gate retenção >60%) e documentado no SKILL.md.
- [x] **P1 #5a** — Hooks auditados nos 5 roteiros 24–28/09; 2 reescritos (`auditoria_gratis`, `negocios_locais`) para ≤8 palavras + número. Backup em `roteiros/.bak-20260924/`.
- [x] **P1 #6** — Comentário CTA postado em 12 vídeos publicados recentes (12/12).
- [x] **P2 #10** — Recheck 26/09 registrado no history (`esteticistas` / `deeDrwxpI3c`).

## Rechecks automáticos
- [ ] **2026-09-26** — `deeDrwxpI3c`: se views==0 → re-up com título vencedor (número+dor+especificidade). Se >0 → avaliar retenção.
- [ ] Gate retenção: 3 vídeos seguidos >60% antes de reativar guardados (38 parked).

## Manual (Studio — inacessível via API)
- [ ] **#8** Impressions/CTR dos 32 agendados (API não expõe `impressions`).
- [ ] **#9** Saúde do canal / audience retention curve por vídeo no Studio.
- [ ] Pin manual do comentário CTA nos 12 vídeos (API não suporta pin).

## Executado em 2026-09-24 (re-render autorizado)
- [x] **#5 real** Re-render dos 2 hooks corrigidos:
  - `hook_video_auditoria_gratis` → **Z7Mz2n8vchk** (25/09 21:00Z); old `nEXalGxclK0` deletado.
  - `hook_video_negocios_locais` → **xclcaUY3-W0** (28/09 21:00Z); old `m_2Cqp8PqiA` deletado.
  - Roteiros: `.bak-20260924/`; mp4s novos em `video-maker/rehook-done/`; thumbs reapontadas.

## Comandos úteis
```bash
python3 ~/.config/opencode/skills/youtube-growth/check_24h.py
```
