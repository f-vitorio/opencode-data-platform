#!/usr/bin/env python3
"""
Check 6h/24h para vídeos publicados recentemente.
Uso:
  python3 check_24h.py            # imprime vídeos elegíveis + métricas
  python3 check_24h.py --window 6  # só janelas de 6h (default: 6 e 24)

Fonte dos elegíveis: YouTube Data API (publicados nas últimas 48h).
O history.json só enriquece (stem/título) — nunca é a fonte da verdade,
senão um history dessincronizado deixa o check cego (bug de 29/09/2026).

Views/likes/comentários: videos.list (statistics) — ao vivo.
Retenção (averageViewPercentage): Analytics API — tem lag de 2-3 dias,
então vídeos recentes podem aparecer com ret=NA.

Não gasta créditos externos; usa o mesmo OAuth da skill.
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from youtube_growth import YouTubeGrowthManager

# BRT = UTC-3 (sem DST no BR)
BRT = dt.timezone(dt.timedelta(hours=-3))
RECENT_H = 48
RETENTION_GATE = 60.0  # %

# Rechecks agendados fora da janela de 48h (file separado de propósito:
# history.json é iterado como {stem: dict} por ~20 trechos de código).
PENDING_FILE = Path(__file__).parent / "pending_checks.json"


def load_pending_checks() -> list:
    if not PENDING_FILE.exists():
        return []
    try:
        data = json.loads(PENDING_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"[Pending] Falha ao ler {PENDING_FILE.name}: {e}")
        return []


def print_due_pending_checks(manager, now_brt) -> list:
    """Seção de rechecks vencidos. Retorna as entradas ainda em aberto."""
    entries = [e for e in load_pending_checks()
               if e.get("status") == "open" and e.get("due")]
    if not entries:
        return []

    today = now_brt.date()
    due = [e for e in entries if dt.date.fromisoformat(e["due"]) <= today]
    future = [e for e in entries if dt.date.fromisoformat(e["due"]) > today]
    if not due:
        print(f"[Pending] {len(future)} recheck(s) futuros; nenhum vencido. "
              f"Próximo: {min(e['due'] for e in future)}")
        return future

    # views ao vivo para as entradas vencidas com vídeo
    ids = [e["video_id"] for e in due if e.get("video_id")]
    live = {}
    for i in range(0, len(ids), 50):
        resp = manager.youtube_service.videos().list(
            part="statistics,status",
            id=",".join(ids[i:i + 50])).execute()
        for v in resp.get("items", []):
            st = v.get("statistics", {})
            live[v["id"]] = dict(
                views=int(st.get("viewCount", 0) or 0),
                privacy=v.get("status", {}).get("privacyStatus", "?"),
            )

    print(f"\n=== RECHECKS VENCIDOS — {now_brt.strftime('%Y-%m-%d')} "
          f"({len(due)}) ===")
    for e in sorted(due, key=lambda x: x["due"]):
        vid = e.get("video_id") or "-"
        l = live.get(vid, {})
        views = l.get("views")
        over = ""
        if e.get("gate") == "views" and views is not None and e.get("threshold") is not None:
            over = ("  ← ACIMA DO LIMITE" if views > e["threshold"]
                    else "  ← ABAIXO DO LIMITE")
        print(f"  [{e['due']}] {e.get('type','?'):22} {vid:14} "
              f"{'v=' + str(views) if views is not None else 'sem vídeo':>10}"
              f"{('  ' + l['privacy']) if l else ''}{over}")
        print(f"      {e.get('note','')}")
        print(f"      id={e.get('id')}")

    if future:
        print(f"  -- adiados: " + ", ".join(
            f"{e['due']} {e.get('video_id') or e.get('type')}" for e in sorted(
                future, key=lambda x: x["due"])))
    print("  Ao concluir: marque status=done em pending_checks.json "
          "e registre o resultado em PENDENTES.md.")
    return due



def recent_public_videos(manager, now_utc, hours=RECENT_H):
    """IDs de vídeos públicos publicados nas últimas `hours` (fonte: API)."""
    ch = manager.youtube_service.channels().list(
        part="contentDetails", mine=True).execute()["items"][0]
    playlist = ch["contentDetails"]["relatedPlaylists"]["uploads"]

    ids, token, seen_pages = [], None, set()
    while True:
        resp = manager.youtube_service.playlistItems().list(
            part="contentDetails", playlistId=playlist, maxResults=50,
            pageToken=token).execute()
        page = tuple(i["contentDetails"]["videoId"]
                     for i in resp.get("items", []))
        if not page or page in seen_pages:
            break  # a API já tinha devolvido esta página (paginação instável)
        seen_pages.add(page)
        ids += list(page)
        token = resp.get("nextPageToken")
        if not token:
            break
    ids = list(dict.fromkeys(ids))  # dedupe

    cutoff = now_utc - dt.timedelta(hours=hours)
    out = []
    for i in range(0, len(ids), 50):
        resp = manager.youtube_service.videos().list(
            part="snippet,status,statistics",
            id=",".join(ids[i:i + 50])).execute()
        for v in resp.get("items", []):
            st = v["status"]
            if st.get("privacyStatus") != "public":
                continue
            iso = v["snippet"].get("publishedAt")
            if not iso:
                continue
            pub_utc = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
            if pub_utc < cutoff:
                continue
            stats = v.get("statistics", {})
            out.append(dict(
                video_id=v["id"],
                title=v["snippet"].get("title", ""),
                published_utc=pub_utc,
                views=int(stats.get("viewCount", 0) or 0),
                likes=int(stats.get("likeCount", 0) or 0),
                comments=int(stats.get("commentCount", 0) or 0),
            ))
    out.sort(key=lambda x: x["published_utc"], reverse=True)
    return out


def report_pending_comments(manager):
    """
    Comentário com CTA + link rastreável: vídeos públicos sem comentário.
    Somente leitura — para aplicar: python3 youtube_growth.py comment <target> --yes
    """
    candidates = [(stem, e) for stem, e in manager.history.items()
                  if isinstance(e, dict)
                  and e.get('video_id')
                  and e.get('status') == 'published'
                  and not e.get('comment_id')]
    if not candidates:
        print("\n[Comentários] Todos os vídeos publicados já têm comentário com CTA.")
        return []

    ids = [e['video_id'] for _, e in candidates]
    public = set()
    for i in range(0, len(ids), 50):
        resp = manager.youtube_service.videos().list(
            part="status", id=",".join(ids[i:i + 50])).execute()
        for v in resp.get("items", []):
            if v.get("status", {}).get("privacyStatus") == "public":
                public.add(v["id"])

    pending = [(stem, e) for stem, e in candidates if e['video_id'] in public]
    skipped = len(candidates) - len(pending)
    if not pending:
        print(f"\n[Comentários] 0 pendente(s) — "
              f"{skipped} ainda não público(s)/sem vídeo.")
        return []

    print(f"\n=== COMENTÁRIOS PENDENTES — {len(pending)} vídeo(s) público(s) "
          f"sem CTA ===")
    for stem, e in sorted(pending, key=lambda x: x[1].get('uploaded_at') or ''):
        print(f"  {stem}  {e['video_id']}  {str(e.get('title', ''))[:55]}")
    print("  Aplicar: python3 youtube_growth.py comment <video> --yes "
          "(fixar no Studio é manual)")
    return pending


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--window', type=int, choices=[6, 24], action='append',
                    help='janela horas (6 e/ou 24); default ambas')
    args = ap.parse_args()
    windows = args.window or [6, 24]

    g = YouTubeGrowthManager()
    if not g.authenticate():
        print("[Check] Falha na autenticação")
        return 1

    now = dt.datetime.now(BRT)
    now_utc = now.astimezone(dt.timezone.utc)

    print_due_pending_checks(g, now)

    videos = recent_public_videos(g, now_utc)
    report_pending_comments(g)
    if not videos:
        print(f'Nenhum vídeo público nas últimas {RECENT_H}h.')
        return 0

    # enriquecimento opcional pelo history (stem)
    stem_by_id = {e.get('video_id'): stem for stem, e in g.history.items()
                  if isinstance(e, dict) and e.get('video_id')}

    for v in videos:
        age = (now_utc - v["published_utc"]).total_seconds() / 3600
        v["age_h"] = age
        v["stem"] = stem_by_id.get(v["video_id"], "-")

    ids = [v["video_id"] for v in videos]
    retention = {}
    try:
        resp = g.analytics_service.reports().query(
            ids='channel==MINE',
            startDate=(now_utc - dt.timedelta(hours=RECENT_H)).strftime('%Y-%m-%d'),
            endDate=now_utc.strftime('%Y-%m-%d'),
            dimensions='video',
            filters='video==' + ','.join(ids),
            metrics='views,likes,comments,averageViewDuration,averageViewPercentage',
        ).execute()
        cols = [c['name'] for c in resp['columnHeaders']]
        for r in resp.get('rows', []):
            d = dict(zip(cols, r))
            retention[d['video.id']] = d
    except Exception as e:
        print(f'[Check] Analytics indisponível (lag/erro): {str(e)[:120]}')

    print(f'=== CHECK — {now.strftime("%Y-%m-%d %H:%M")} BRT | '
          f'públicos nas últimas {RECENT_H}h: {len(videos)} ===')

    fails, known = [], 0
    for v in videos:
        vid = v["video_id"]
        m = retention.get(vid, {})
        has_ret = vid in retention
        avp = float(m.get('averageViewPercentage', 0) or 0)
        avd = float(m.get('averageViewDuration', 0) or 0)
        # views ao vivo (statistics) — analytics tem lag
        views = v["views"]
        likes = v["likes"]
        comments = v["comments"]

        if has_ret:
            known += 1
            gate = 'PASS' if avp >= RETENTION_GATE else 'FAIL'
            if gate == 'FAIL':
                fails.append(vid)
            ret_str = f'ret={avp:5.1f}%'
            dur_str = f'dur={avd:4.1f}s'
        else:
            gate = 'NA'   # sem dados de retenção ainda (lag)
            ret_str = 'ret=  N/A'
            dur_str = 'dur= N/A'

        due = [w for w in windows if v["age_h"] >= w]
        flag = ' '.join(f'{w}h✓' for w in due) if due else ''
        title = v["title"][:50]
        print(f'[{flag or "--"}] {v["age_h"]:5.1f}h  {gate:>4}  '
              f'{ret_str}  {dur_str}  '
              f'v={views:<5} l={likes:<3} c={comments:<3}  {vid}  {title}')

    print(f'\nGate retenção >{RETENTION_GATE}%: {known - len(fails)}/{known} PASS'
          + (f' | FAIL: {", ".join(fails)}' if fails else '')
          + (f' | NA (sem retenção ainda): {len(videos) - known}' if len(videos) - known else ''))
    if fails:
        print('Ação: analisar a curva de retenção desses IDs no Studio '
              'antes de escalar/reativar agendamentos.')
    if len(videos) - known:
        print('NA = Analytics ainda sem retenção para o vídeo (lag 2-3 dias). '
              'Repetir o check em 48h.')


if __name__ == '__main__':
    main()
