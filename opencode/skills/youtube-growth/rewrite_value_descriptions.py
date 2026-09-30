#!/usr/bin/env python3
"""
Ação 5 — reescreve a DESCRIÇÃO dos Shorts agendados: troca o bloco de
credenciais por linhas de valor tiradas do roteiro que gerou o vídeo.

O que faz por vídeo:
  1. Seleciona só os scheduled ATIVOS (ignora replaced_by / cancelled).
  2. Monta a nova descrição: título (inalterado) + 3 linhas de valor do
     roteiro + link de CTA com UTM (inalterado) + hashtags (inalteradas).
  3. Roda seo_audit() no resultado — se não PASSAR, não envia (relata).
  4. Envia via update_metadata() (preserva privacidade e publishAt).
  5. Reescreve a seção DESCRIÇÃO do .txt local.

Linhas de credenciais removidas:
  ✅ Ads especialistas | ✅ landing page rápida (LCP1s) | ...
  📊 +150 projetos | 4.9/5 | 100% GTmetrix

Uso:
  python3 rewrite_value_descriptions.py                 # dry-run (default)
  python3 rewrite_value_descriptions.py --examples 2    # dry-run, 2 exemplos completos
  python3 rewrite_value_descriptions.py --apply         # executa
  python3 rewrite_value_descriptions.py --apply --stems outubro_08_lp_conversao_6x
"""
import argparse
import re
import sys
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from youtube_growth import YouTubeGrowthManager, DELIMITER

ROTEIROS_DIR = Path.home() / "video-maker" / "roteiros"
ROTEIRO_OCT = ROTEIROS_DIR / "outubro-2026"

# Linhas que nunca viram corpo de descrição
CTA_RE = re.compile(r"acesse|acessar|fvs7\.com\.br|diagnóstico|diagnostico|"
                    r"solicite|peça\b|solicitar", re.I)
BRAND_RE = re.compile(r"^fvs7(\s+marketing\s+digital)?$", re.I)
BOILER_RE = re.compile(r"^\s*[✅📊👉]\s*(Ads especialistas|.*projetos|Diagnóstico)", re.I)
# Passos numerados / listas: pegar 3 linhas destas corta a lista no meio
STEP_RE = re.compile(r"(primeiro|segundo|terceiro|quarto|quinto|regra\s+\w+|erro\s+número|erro\s+\d)",
                     re.I)
# Preferência por frases que sustentam sentido sozinhas
PREFERRED_MIN_WORDS = 6
FALLBACK_MIN_WORDS = 4


# ── mapeamento stem → arquivo de roteiro ────────────────────────────────────
def find_roteiro(stem: str) -> Optional[Path]:
    if stem.startswith("outubro_"):
        # outubro_08_lp_conversao_6x  →  outubro-2026/08_lp_conversao_6x.txt
        slug = stem[len("outubro_"):]
        cand = ROTEIRO_OCT / f"{slug}.txt"
        if cand.exists():
            return cand
    # nomes legados da pasta roteiros/
    legacy = {
        "hook_video_esteticistas": ["roteiro_esteticistas.txt", "video_esteticistas.txt"],
        "hook_video_fisioterapeutas": ["video_fisioterapeutas.txt"],
        "hook_video_imobiliarias": ["video_imobiliarias.txt"],
    }
    for name in legacy.get(stem, []):
        cand = ROTEIROS_DIR / name
        if cand.exists():
            return cand
    return None


def existing_value_lines(description: str, title: str) -> list:
    """Corpo de valor já escrito à mão no YouTube (antes do bloco de credenciais).
    Se existir, tem prioridade sobre a extração automática do roteiro."""
    out = []
    for line in description.splitlines():
        t = line.strip()
        if not t or t == title:
            continue
        if "utm_content=" in t or t.startswith("#"):
            continue
        if BOILER_RE.match(t) or t.startswith(("✅", "📊")):
            continue
        out.append(t)
    return out


def ensure_terminal_period(line: str) -> str:
    if line[-1] in ".!?;:…":
        return line
    return line + "."


def extract_value_lines(roteiro: Path, limit: int = 3) -> list:
    """Linhas de corpo da descrição.

    Descarta: hook (linha 1, já coberto pelo título), CTA, assinatura da marca,
    bloco de credenciais, perguntas retóricas e passos numerados (que precisariam
    da lista inteira). Depois prefere frases de ≥6 palavras; se faltar, relaxa
    para ≥4 em vez de devolver corpo incompleto.
    """
    raw = [l.strip() for l in roteiro.read_text(encoding="utf-8").splitlines()]
    paras = [l for l in raw if l]          # descarta linhas vazias

    candidates = []
    for line in paras[1:]:                 # [0] é o hook = já coberto pelo título
        words = line.split()
        if len(words) < FALLBACK_MIN_WORDS:
            continue
        if line.endswith("?"):
            continue
        if CTA_RE.search(line) and len(words) <= 12:
            continue
        if BRAND_RE.match(line) or BOILER_RE.match(line):
            continue
        if STEP_RE.search(line):
            continue
        candidates.append(ensure_terminal_period(line))

    preferred = [l for l in candidates if len(l.split()) >= PREFERRED_MIN_WORDS]
    chosen = preferred[:limit]
    if len(chosen) < limit:
        for line in candidates:
            if len(chosen) >= limit:
                break
            if line not in chosen:
                chosen.append(line)

    # "Antes"/"Depois" só faz sentido em par — nunca publicar um sem o outro
    if any(l.lower().startswith("depois") for l in chosen):
        par = [l for l in candidates if l.lower().startswith("antes")]
        for line in par:
            if line not in chosen:
                chosen.insert(0, line)

    return chosen


def extract_cta_and_tags(description: str) -> tuple:
    """Preserva a linha de CTA com UTM e as hashtags originais."""
    cta, tags = None, []
    for line in description.splitlines():
        t = line.strip()
        if not t:
            continue
        if "utm_content=" in t:
            cta = t
        elif t.startswith("#"):
            tags.append(t)
    return cta, tags


def build_description(title: str, roteiro: Path, old_desc: str) -> tuple:
    """(nova descrição, lista de linhas de valor) | (None, motivo) quando falha."""
    # 1) o que já foi escrito à mão tem prioridade (evita piorar copy boa)
    value = existing_value_lines(old_desc, title)
    source = "manuscrita"
    # 2) senão extrai do roteiro que gerou o vídeo
    if not value:
        value = extract_value_lines(roteiro)
        source = roteiro.name
    if not value:
        return None, [], f"sem linhas de valor extraíveis de {roteiro.name}"

    cta, tags = extract_cta_and_tags(old_desc)

    parts = [title, ""]
    parts += value
    if cta:
        parts += ["", cta]
    if tags:
        parts += ["", " ".join(tags)]

    return "\n".join(parts), value, source


def rewrite_txt_section(text: str, header: str, new_content: str):
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="executa (default: dry-run)")
    ap.add_argument("--examples", type=int, default=0,
                    help="mostra N descrições completas no dry-run")
    ap.add_argument("--stems", help="lista separada por vírgula de stems")
    ap.add_argument("--sleep", type=float, default=0.4, help="pausa entre chamadas de API")
    args = ap.parse_args()

    manager = YouTubeGrowthManager()
    plan, skipped, blocked = [], [], []

    for stem, entry in manager.history.items():
        if not isinstance(entry, dict) or entry.get("status") != "scheduled":
            continue
        if not entry.get("video_id"):
            continue
        if args.stems and stem not in {x.strip() for x in args.stems.split(",")}:
            continue
        if entry.get("replaced_by"):
            skipped.append((stem, f"substituído por {entry['replaced_by']} "
                                  f"({entry.get('pending_cancel_reason') or 'cancelled'})"))
            continue

        old = entry.get("description") or ""
        if "✅ Ads especialistas" not in old and "📊 +150 projetos" not in old:
            skipped.append((stem, "já sem bloco de credenciais"))
            continue

        roteiro = find_roteiro(stem)
        if roteiro is None:
            blocked.append((stem, entry, "roteiro não encontrado"))
            continue

        new_desc, value, source = build_description(entry.get("title", ""), roteiro, old)
        if new_desc is None:
            blocked.append((stem, entry, source))
            continue

        errors = manager.seo_audit(entry.get("title", ""), new_desc)
        if errors:
            blocked.append((stem, entry, "; ".join(errors)))
            continue

        plan.append((stem, entry, new_desc, value, source))

    print(f"[Ação-5] plano: {len(plan)} descrições | {len(blocked)} bloqueadas | "
          f"{len(skipped)} ignoradas")
    for stem, why in skipped:
        print(f"    [skip] {stem}: {why}")

    for stem, entry, why in blocked:
        print(f"\n  BLOQUEADO {stem} ({entry.get('video_id')}): {why}")

    # ── preview ─────────────────────────────────────────────────────────────
    show = plan[: max(args.examples, 0)] if args.examples else plan[:3]
    for stem, entry, new_desc, value, rname in show:
        print(f"\n{DELIMITER}")
        print(f"  {entry['video_id']}  {stem}   ← {rname}")
        print(DELIMITER)
        print("── DESCRIÇÃO ATUAL " + "─" * 44)
        print(entry.get("description") or "(vazio)")
        print("── NOVA DESCRIÇÃO " + "─" * 45)
        print(new_desc)
        print("── linhas de valor: " + str(len(value)) + " ─" * 12)

    if plan and not args.examples:
        print(f"\n(3 primeiras mostradas; use --examples N para ver mais)")

    if not args.apply:
        print(f"\n[Ação-5] DRY-RUN — nada foi alterado. "
              f"Rode com --apply para executar as {len(plan)} alterações.")
        return 0

    ok = fail = 0
    failures = []
    for stem, entry, new_desc, _value, _rname in plan:
        try:
            success = manager.update_metadata(entry["video_id"], entry.get("title", ""),
                                              new_desc, add_utm=True)
        except Exception as e:
            success = False
            print(f"[Ação-5] erro {entry['video_id']}: {e}")
        if not success:
            fail += 1
            failures.append(entry["video_id"])
            continue
        ok += 1

        mf = entry.get("metadata_file")
        if mf and Path(mf).exists():
            try:
                text = Path(mf).read_text(encoding="utf-8")
                new_text = rewrite_txt_section(text, "DESCRIÇÃO (copie e cole)", new_desc)
                if new_text:
                    Path(mf).write_text(new_text, encoding="utf-8")
                else:
                    print(f"[Ação-5] .txt sem seção DESCRIÇÃO: {mf}")
            except Exception as e:
                print(f"[Ação-5] falha ao atualizar {mf}: {e}")
        time.sleep(args.sleep)

    print(f"\n[Ação-5] aplicados: {ok} | falhas: {fail}")
    if failures:
        print(f"[Ação-5] video_ids com falha: {', '.join(failures)}")

    remaining = sum(
        1 for e in manager.history.values()
        if isinstance(e, dict)
        and e.get("status") == "scheduled"
        and not e.get("replaced_by")
        and "✅ Ads especialistas" in (e.get("description") or "")
    )
    print(f"[Ação-5] scheduled ativos ainda com bloco de credenciais: {remaining}")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
