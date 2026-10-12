# TESTE — Lote-piloto de padrão de roteiro (retenção)

Criado: 2026-10-06 | Janela: publicação 07–13/10/2026 | Leitura: 14–20/10

## Hipótese

O novo padrão de roteiro (65–75 palavras, hook afirmativo ≤8 palavras com número e
dor, 6 segmentos curtos, sem URL falada, ≤30s, CTA de marca só após 3s) eleva a
retenção média do Short em relação ao padrão anterior dos mesmos temas.

## Condições

- **Tratamento (piloto):** 7 vídeos, 1/dia às **18:00 BRT (21:00Z)**, 07–13/10.
- **Controle:** 7 vídeos, 1/dia às **12:00 BRT (15:00Z)**, 07–13/10, padrão antigo.
- Mesmo canal, mesma janela, mesmo volume. Horário é variável de controle, não de teste.
- Os 7 slots antigos das 18h (07–13/10) foram **cancelados** (voltaram a `private`,
  status `uploaded`) para liberar o horário — re-agendar após 13/10 (ver PENDENTES.md).

## Tratamento (piloto) vs baseline

Baseline = retenção média já medida (14 dias) do vídeo publicado do mesmo tema.

| Dia | Hora BRT | Piloto | video_id | Tema | Baseline retenção | Views base |
|-----|----------|--------|----------|------|-------------------|-----------|
| 07/10 | 18:00 | piloto_01_psicologos | `eKzogqwLXgk` | psicólogos | **24,0%** | 20 |
| 08/10 | 18:00 | piloto_02_landing_page_conversao | `9D8-_9pL4OQ` | landing page conversão | **24,8%** | 73 |
| 09/10 | 18:00 | piloto_03_advogados | `bxyVcvzezB8` | advogados | **14,0%** | 80 |
| 10/10 | 18:00 | piloto_04_fisioterapeutas | `Rtq5sWfxGT4` | fisioterapeutas | **16,7%** | 48 |
| 11/10 | 18:00 | piloto_05_negocios_locais | `GEVKydtk2rE` | negócios locais | **67,5%** | 12 |
| 12/10 | 18:00 | piloto_06_clinicas | `K5Mpw3g9O7w` | clínicas | **21,3%** | 6 |
| 13/10 | 18:00 | piloto_07_trafego_pago | `cgNkHGxvF0E` | tráfego pago | **147,7%** | 19 |

Gate de retenção do teste: **>60%** (mesmo gate de `check_24h.py`).

## Controle (12:00 BRT) na mesma janela

| Dia | video_id | stem | Título |
|-----|----------|------|--------|
| 07/10 | `KULpdQ9m6xE` | outubro_11_google_ads_reduzir_cpc | Google Ads: Estratégia para Reduzir CPC em 40% |
| 08/10 | `UnCQad3U0QI` | outubro_13_lp_antes_depois | Landing Page: Case 6x - Antes e Depois |
| 09/10 | `g-vckNe5r8o` | outubro_15_google_ads_5_dicas_roi | Google Ads: 5 Dicas para Dobrar seu ROI |
| 10/10 | `yLyVwASnjqg` | outubro_17_trafego_pago_guia | Tráfego Pago: Guia Definitivo para Iniciantes |
| 11/10 | `sdHuAT7vDqc` | outubro_19_google_ads_copy_cpc | Google Ads: Copy que Converte - Fórmulas Testadas |
| 12/10 | `SNOZj1G6Lak` | outubro_21_lp_3_erros_orcamento | Landing Page: 3 Erros que Fazem Perder Orçamento |
| 13/10 | `UhEAIsiXEyc` | outubro_30_google_ads_vs_facebook | Google Ads vs Facebook Ads: Onde Investir Primeiro |

Atenção (ruído): `outubro_23_google_ads_segmentacao` (`QKGhztZj3e0`) está em
12/10 18:00Z (15:00 BRT) — terceiro vídeo naquele dia, fora dos dois braços.

## Como medir (leitura em 14–20/10)

1. `python3 check_24h.py` → views ao vivo + retenção Analytics (NA no lag de ~2 dias).
2. Comparar retenção piloto × baseline do mesmo tema (coluna acima).
3. Comparar piloto × controle da mesma semana (mesma faixa de horário diferente).
4. Decisão: se ≥4 de 7 pilotos superam a baseline **e** a média do grupo > média do
   controle → adotar o padrão como padrão oficial da próxima leva.

## Aprendizado técnico do lote

- `schedule`/`schedule-existing` gravam o horário informado **direto no `publishAt`
  como UTC** (`strftime(...%fZ)`), sem converter fuso. Para 18:00 BRT é preciso passar
  **21:00**. Os 7 primeiros agendamentos saíram às 15:00 BRT e foram corrigidos com
  `schedule-existing` para 21:00Z; verificado via `videos.list(status.publishAt)`.
- Título/descrição gerados pelo `make_video.py` saem genéricos e errados por tema
  (ex.: "Tracking: Quanto Cada Lead Custa" num vídeo de psicólogos) + têm bloco
  `✅ +150 projetos` que a Ação 5 removeu. Copy escrita manualmente por tema antes do
  `seo-audit`.
- `history.json` tem convenção **mista** em `scheduled_at`: o que é gravado por
  `schedule`/`schedule-existing` é o horário passado em `--when` (naive = UTC);
  o que é gravado por `sync_history.py` passa por `to_brt()` (BRT). 60 entradas
  agendadas estão todas em horário cheio = escritas pelos scripts (UTC).
  Para 18:00 BRT, ler `21:00` no `history` (igual ao `publishAt` da API).
- Delimitador do `.txt` de metadados precisa ter **63** caracteres `═`
  (`DELIMITER = "═" * 63`); com 64 o parser não acha o título → "Título vazio".
