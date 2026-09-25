# Relatório de Desempenho — Canal YouTube Shorts (FVS7 Growth)

**Data:** 23/09/2026
**Fontes:** YouTube Analytics API (últimos 30/60 dias), `history.json` (79 vídeos), arquivos `.txt`/`.mp4` da `video-creator` (92 pares)

---

## 1. Números reais (fatos)

| Métrica (30 dias) | Valor |
|---|---|
| Views totais | **150** |
| Watch time | 10 min |
| Duração média de visualização | 15s |
| Retenção média | **47,8%** |
| Likes | 2 |
| Comentários | **0** |
| Shares | 0 |
| Subscribers ganhos | **1** |
| Views de inscritos | **0** (156 de não-inscritos) |

**Distribuição por vídeo (topo):**
- `ds8O7QfE6EA` (Clínicas): 105 views, 41,7% retenção, 9s duração média
- Demais: 14, 9, 8, 7, 6, 2, 2, 1 views — o resto do catálogo: **0**

**Tráfego (60 dias):**
- Shorts feed: 95 views | YouTube Search: 51 | Inscritos: 6 | Externo: 2
- Dispositivo: 83% mobile | País: BR

**Curva de retenção do melhor vídeo (`ds8O7QfE6EA`):**
~100% até 16% do vídeo → **queda para 47% aos 31% → 21% aos 41%** → platô em 15%.
Ou seja: **metade da audiência sai nos primeiros ~5–8 segundos.**

**Histórico local (`history.json`):**
- 79 vídeos: 3 `published`, 76 `scheduled`
- Lote `outubro_01` a `outubro_51`: `scheduled_at = null` e **0 views no Analytics** — indício forte de que nunca foram publicados (ficaram privados). Verificar no YouTube Studio.
- Vídeos agendados 22–23/09 com views baixas (32, 5, 5, 5) → agendamento funcionou para o lote de setembro, mas status local está desatualizado.

**Conteúdo (92 arquivos `.txt`):**
- **92/92** contêm o mesmo pitch publicitário da agência ("Google Ads gerenciado por especialistas...", +150 projetos, 4.9/5, GTmetrix)
- Duração dos vídeos: ~48–59s (ok para Shorts), 1080×1920 (ok)
- Títulos: média 48 caracteres, template fixo `[Nicho]: [Número] + [Benefício]`

**Operação:**
- Hiato de 7 meses (mar–ago/2026) antes da retomada
- Meta do plano: 1.000 subs em 60 dias e 50.000 views/mês — sem baseline compatível
- Cota da YouTube Data API v3 **estourada** hoje (análises automatizadas ficam cegas)

---

## 2. Diagnóstico — por que os vídeos não têm views

### Causa 1 — O teste inicial do Shorts falha (retenção) 🔴
O algoritmo distribui o Short para uma audiência-teste pequena. Com retenção de 41–48% e queda brutal nos primeiros segundos, o YouTube **corta a distribuição**. Isso explica o teto de ~5–105 views: o vídeo não é "enterrado", ele é **reprovado no teste**.

**Evidência:** 95 views vêm do Shorts feed, mas só 8 vídeos tiveram qualquer view — os demais não passaram (ou não foram publicados).

### Causa 2 — Conteúdo 100% publicitário, sem valor puro 🔴
92/92 descrições são anúncio da agência. O Short não entrega conhecimento/entretenimento; entrega pitch. Audiência fria no Shorts não tolera publicidade nos primeiros segundos — e o CTA de link na descrição não é como Shorts convertem.

**Resultado:** 0 comentários, 0 shares, 1 subscriber em 30 dias. Sem sinal de engajamento, o algoritmo não tem por que escalar.

### Causa 3 — Lote outubro possivelmente nunca publicado 🔴
`outubro_01`–`outubro_51` estão com `scheduled_at = null` e 0 views. Se estão privados no Studio, **mais da metade do catálogo produzido não está no ar**. Isso é a causa mais fácil de corrigir e precisa ser verificado primeiro.

### Causa 4 — Canal sem base + hiato de 7 meses 🟡
Antes do hiato: 11.574 views e melhor vídeo com 8.896. Após 7 meses parado, o canal perdeu tração. 0 views de inscritos mostra que não há audiência recorrente para alimentar o teste inicial.

### Causa 5 — Volume sem ciclo de aprendizado 🟡
2 vídeos/dia com o mesmo formato, sem iterar com dados (o próprio plano prevê medir em 7 dias e ajustar — isso não está acontecendo). Escalar erro = escalar resultado de 0.

### Causa 6 — Operação secundária 🟡
- Cota da API estourada (sem auditoria/analytics automatizados)
- Horários 06:00 no calendário, enquanto o próprio checklist indica pico 12–14h / 18–20h
- Histórico local dessincronizado do estado real no YouTube
- Sem comentários fixados (o `comments.txt` existe mas 0 comentários no canal sugere que o plano de CTA não foi executado)

---

## 3. O que pode ser melhorado (priorizado)

### Imediato (hoje / 48h)
1. **Verificar no YouTube Studio quais vídeos do lote `outubro_01`–`outubro_51` estão privados** e publicar os que foram esquecidos (ou agendar corretamente).
2. **Corrigir o `history.json`** para refletir o estado real (vídeos de setembro já publicados; outubro pendente).
3. **Resolver a cota da API** (ou aguardar reset diário) para retomar auditoria automática.

### Conteúdo (alavanca principal)
4. **Hook nos primeiros 2 segundos** — o vídeo atual perde metade da audiência em ~5s. Regra: problema/ponto de dor ou promessa específica imediata, nunca logo/marca/pitch.
5. **Trocar o formato "anúncio" por "valor + prova"**:
   - 80% do vídeo: dica, erro comum, antes/depois, número real de cliente
   - 20% no máximo: marca/CTA
   - Mover o boilerplate da agência **para fora** das descrições (manter 1–2 linhas + link)
6. **CTA de engajamento falado no vídeo** ("Qual desses 3 erros você comete? Comenta") — meta mínima: 1º comentário fixado em cada vídeo (o `comments.txt` já tem os textos; falta executar).
7. **Testar 2–3 formatos diferentes** por 2 semanas em vez de escalar o mesmo template: (a) erro→consequência→solução, (b) antes/depois com tela, (c) myth-busting rápido.

### Distribuição
8. **Publicar no pico real:** 12–14h e 18–20h (BR), abandonar 06:00 como padrão.
9. **Reduzir volume para 1 vídeo/dia** até o formato passar no teste (meta interna: retenção >60% e ≥100 views consistente), depois voltar a escalar.
10. **Comentar/respondo nas primeiras 2–4h** após publicar para sinalizar engajamento.

### Metas realistas
11. Revisar metas do `content-plan.md`: de 50.000 views/mês para **marcos por fase** — ex.: 1.000 views/mês → 10k → 50k, com critérios de formato a replicar quando um vídeo passar de 1.000 (o próprio plano já define "viral >10k = replicar formato").

### SEO do Short
12. Títulos ok (≤60 chars), mas trocar genéricos por **especificidade com número/resultados** já previstos no plano e não aplicados de forma consistente.
13. Manter #Shorts + 3–5 hashtags temáticas (hoje ok); evitar linha inteira de hashtags na descrição (manter no fim).

---

## 4. Resumo em uma frase

**Os vídeos não têm views porque (a) metade do catálogo pode não estar publicada, (b) quem assiste sai nos primeiros 5 segundos (retenção ~45%), e (c) o conteúdo é 100% publicitário e gera 0 engajamento — o algoritmo testa, reprova e para de distribuir.**

Prioridade: publicar o que está esquecido → reescrever hook/roteiro com valor puro → medir retenção por 7 dias antes de escalar volume.
