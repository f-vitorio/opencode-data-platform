#!/usr/bin/env python3
"""
Correção em lote da REGRA INVIOLÁVEL de SEO em vídeos publicados e programados.

O que faz por vídeo (status published/scheduled):
  1. Título: aplica o título corrigido (mapa curado) e expande abreviações.
  2. Descrição: expande abreviações e garante que a 1ª linha comece com keyword.
  3. Roda seo_audit() no resultado — se não PASSAR, não envia (relata).
  4. Envia via update_metadata() (preserva privacidade e publishAt do agendado).
  5. Reescreve as seções TÍTULO/DESCRIÇÃO do .txt local (quando existir).

Uso:
  python3 fix_metadata_seo.py            # dry-run (só mostra o plano)
  python3 fix_metadata_seo.py --apply    # executa as alterações
  python3 fix_metadata_seo.py --apply --only published
  python3 fix_metadata_seo.py --apply --only scheduled
  python3 fix_metadata_seo.py --apply --only uploaded
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from youtube_growth import YouTubeGrowthManager, DELIMITER

# ── Títulos corrigidos (revisão manual): keyword por extenso no início, ≤50 chars
TITLE_FIXES = {
    "Fy1xYBekxqY": "Landing Page: O Que Faz Converter 6x Mais",
    "Vn0N-V7f-3U": "Clínicas: 50 Agendamentos/Mês com Esse Método",
    "lzVs8fsibcs": "Captação de Clientes: 3x Mais Leads PJ",
    "DIVc777Wuhg": "Psicólogos: Captação Ética — O Caminho Certo",
    "o2kDyCQRJLU": "Conversão: Formulário Perde Leads? 3 Princípios",
    "TI-iFAZVk_E": "Estética: Lotar a Agenda com 50 Procedimentos",
    "jgun_Cv8GFk": "Google Meu Negócio: Clientes Locais em 7 Dias",
    "l6aDZgqsmlU": "Clínicas: De Agenda Vazia a Lotada (Case Real)",
    "LwTUFYEL_pA": "Google Ads: Quality Score 10/10, Pague Menos",
    "Fq81qncfSSM": "Landing Page: LCP de 1 Segundo Converte Mais",
    "Yaezel11-6w": "Google Ads: Orçamento Queima? Erros de Iniciante",
    "RCQ32O7sxag": "Landing Page: A/B Test — O Que Testar Primeiro",
    "OTkXCK4Dt6c": "Conversão: CTA Some no Scroll? 3 Botões que Param",
    "grL6Czd_io0": "Leads: Capte 3x Mais com Diagnóstico Grátis",
    "qmdEBzBMSsQ": "Landing Page Mobile: 95% do Tráfego é Celular",
    "AH8DQhw7Pnw": "Imobiliária: Venda na Planta com a Página Certa",
    "FXNPSdZy14U": "Landing Page: 3 Elementos de Oferta que Vendem",
    "pwXnJ6eRipc": "Estética: Lotar a Agenda na Black Friday",
    "4VCwI9frZxU": "Clínicas: Promoção Certa Enche a Agenda (Case)",
    "o4DC6Qc2qrY": "Google Ads: Resultados Reais que Pagam a Conta",
    "KiDBeTL4p9g": "Google Ads: CPL Oculto Deixa o Lead Mais Caro",
    "WVPyhmqFNkg": "Landing Page Lenta: 53% dos Cliques Morrem",
    "xclcaUY3-W0": "Google Meu Negócio: 5 Estrelas = Clientes",
    "R3xonKBmeyA": "Google Ads + Landing Page: Resultados Reais",
    "N7AyjhEd_qE": "Google Ads: Transforme Cliques em Clientes",
    "tH_jbKIOi8g": "Google Ads: Desperdício que Custa R$5.000/Mês",
    "3XhjuXiDCHA": "Google Ads: 3 Erros de Cliques sem Vendas",
    "K0mF3SuFd0U": "Conversão: Como Transformar Cliques em Clientes",
    "YF_fkkCHp5M": "Landing Page Não Vende? Este Erro Queima Orçamento",
}

# ── Abreviações → forma por extenso (mesma lista da auditoria)
ABBREV_REPLACEMENTS = [
    (re.compile(r"\bLPs\b", re.I), "landing pages"),
    (re.compile(r"\bLP\b", re.I), "landing page"),
    (re.compile(r"\bMKT\b", re.I), "marketing"),
    (re.compile(r"\bCONV\b", re.I), "conversão"),
    (re.compile(r"\bCAP\.?\b", re.I), "captação"),
    (re.compile(r"\bCLI\.?\b", re.I), "cliente"),
    (re.compile(r"\bPÁG\.?\b", re.I), "página"),
]


def expand_abbreviations(text: str) -> str:
    for pattern, correct in ABBREV_REPLACEMENTS:
        text = pattern.sub(correct, text)
    return text


def rewrite_section(text: str, header: str, new_content: str):
    """Reescreve o conteúdo entre `header` e o próximo delimitador. None se não achar."""
    lines = text.split("\n")
    idx = next((i for i, line in enumerate(lines) if header in line), None)
    if idx is None:
        return None
    if idx + 1 >= len(lines) or lines[idx + 1] != DELIMITER:
        lines.insert(idx + 1, DELIMITER)
    start = idx + 2
    end = next((i for i in range(start, len(lines)) if lines[i] == DELIMITER), None)
    if end is None:
        return None
    lines[start:end] = [""] + new_content.split("\n") + [""]
    return "\n".join(lines)


def build_fix(manager: YouTubeGrowthManager, entry: dict):
    video_id = entry.get("video_id")
    old_title = entry.get("title", "") or ""
    old_desc = entry.get("description", "") or ""

    title = expand_abbreviations(TITLE_FIXES.get(video_id, old_title))

    # o título precisa passar na auditoria; senão o vídeo fica para revisão manual
    title_errors = manager.seo_audit(title, "")
    if title_errors:
        return None, None, title_errors

    desc = expand_abbreviations(old_desc)
    pulled_from_live = False
    if not desc.strip():
        # histórico sem descrição: usa a descrição que está no YouTube
        live = manager.get_video_status(video_id).get("description") or ""
        desc = expand_abbreviations(live)
        pulled_from_live = True

    lines = desc.split("\n")
    idx = next((i for i, line in enumerate(lines) if line.strip()), None)

    if idx is None:
        desc = title
    else:
        probe = manager.seo_audit(title, lines[idx].strip())
        if any(e.startswith("Descrição") for e in probe):
            if pulled_from_live:
                # preserva o conteúdo que só existe no YouTube: prefixa o título
                desc = title + "\n\n" + desc.lstrip("\n")
            else:
                lines[idx] = title
                desc = "\n".join(lines)

    errors = manager.seo_audit(title, desc)
    return title, desc, errors, {"pulled": pulled_from_live, "live": live if pulled_from_live else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="executa (default: dry-run)")
    ap.add_argument("--only", choices=["published", "scheduled", "uploaded", "deleted"], help="filtra por status")
    ap.add_argument("--stems", help="lista separada por vírgula de stems do history")
    ap.add_argument("--sleep", type=float, default=0.4, help="pausa entre chamadas de API")
    args = ap.parse_args()

    manager = YouTubeGrowthManager()
    plan, blocked, unchanged = [], [], []

    for stem, entry in manager.history.items():
        if not isinstance(entry, dict):
            continue
        if entry.get("status") not in ("published", "scheduled", "uploaded", "deleted") or not entry.get("video_id"):
            continue
        if args.only and entry.get("status") != args.only:
            continue
        if args.stems and stem not in {x.strip() for x in args.stems.split(",")}:
            continue
        local_errors = manager.seo_audit(entry.get("title", ""), entry.get("description", ""))
        if local_errors or not (entry.get("description") or "").strip():
            pass  # precisa de correção (ou descrição ausente no histórico)
        else:
            unchanged.append(stem)
            continue

        title, desc, errors, meta = build_fix(manager, entry)
        if errors or title is None:
            blocked.append((stem, entry, errors))
            continue

        # descrição só no YouTube e já dentro do padrão: sincroniza o history sem chamar a API
        if meta["pulled"] and desc == meta["live"] and title == entry.get("title"):
            entry["description"] = meta["live"]
            manager.save_history()
            unchanged.append(stem)
            continue

        if title == entry.get("title") and desc == entry.get("description"):
            unchanged.append(stem)
            continue
        plan.append((stem, entry, title, desc))

    print(f"[SEO-fix] plano: {len(plan)} correções | {len(blocked)} bloqueadas | "
          f"{len(unchanged)} já ok")

    for stem, entry, title, desc in plan:
        marker = "TÍTULO→" if title != entry.get("title") else "SÓ DESC→"
        print(f"\n  {entry['video_id']} [{entry['status']}] {stem}")
        if title != entry.get("title"):
            print(f"    {marker} {entry.get('title')}")
            print(f"         → {title}")
        first_old = (entry.get("description") or "").split("\n")[0]
        first_new = desc.split("\n")[0]
        if first_new != first_old:
            print(f"    DESC 1ª linha: {first_old[:70]}")
            print(f"             → {first_new[:70]}")
        if "landing page" in desc and "LP" in (entry.get("description") or ""):
            print("    DESC: abreviações LP expandidas")

    for stem, entry, errors in blocked:
        print(f"\n  BLOQUEADO {entry['video_id']} — {entry.get('title')}")
        for e in errors:
            print(f"      - {e}")

    if not args.apply:
        print("\n[SEO-fix] DRY-RUN — nada foi alterado. Rode com --apply para executar.")
        return 0

    ok = fail = 0
    failures = []
    for stem, entry, title, desc in plan:
        try:
            success = manager.update_metadata(entry["video_id"], title, desc, add_utm=True)
        except Exception as e:
            success = False
            print(f"[SEO-fix] erro {entry['video_id']}: {e}")
        if not success:
            fail += 1
            failures.append(entry["video_id"])
            continue
        ok += 1
        # sincroniza o .txt local
        mf = entry.get("metadata_file")
        if mf and Path(mf).exists():
            try:
                text = Path(mf).read_text(encoding="utf-8")
                new_text = rewrite_section(text, "TÍTULO (para YouTube Shorts / Reels / TikTok)", title)
                if new_text:
                    new_text = rewrite_section(new_text, "DESCRIÇÃO (copie e cole)", desc) or new_text
                    Path(mf).write_text(new_text, encoding="utf-8")
                else:
                    print(f"[SEO-fix] .txt sem seção TÍTULO: {mf}")
            except Exception as e:
                print(f"[SEO-fix] falha ao atualizar {mf}: {e}")
        time.sleep(args.sleep)

    print(f"\n[SEO-fix] aplicados: {ok} | falhas: {fail}")
    if failures:
        print(f"[SEO-fix] video_ids com falha: {', '.join(failures)}")

    # auditoria final
    remaining = sum(
        1 for e in manager.history.values()
        if isinstance(e, dict)
        and e.get("status") in ("published", "scheduled")
        and manager.seo_audit(e.get("title", ""), e.get("description", ""))
    )
    print(f"[SEO-fix] restantes fora do padrão (published+scheduled): {remaining}")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
