#!/usr/bin/env python3
"""
Check 6h/24h para vídeos publicados recentemente.
Uso:
  python3 check_24h.py            # imprime vídeos elegíveis + métricas
  python3 check_24h.py --window 6  # só janelas de 6h (default: 6 e 24)
Lógica: para cada vídeo com published_at nas últimas 48h, puxa views/likes/
comentários da Analytics API e imprime gate de retenção (>60% = PASS).
Não gasta créditos externos; usa o mesmo OAuth da skill.
"""
import argparse, sys, os, datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from youtube_growth import YouTubeGrowthManager

# BRT = UTC-3 (sem DST no BR)
BRT = dt.timezone(dt.timedelta(hours=-3))
RECENT_H = 48
RETENTION_GATE = 60.0  # %


def parse_brt(s: str):
    # history guarda published_at naive local BRT
    return dt.datetime.fromisoformat(s).replace(tzinfo=BRT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--window', type=int, choices=[6, 24], action='append',
                    help='janela horas (6 e/24); default ambas')
    ap.add_argument('--channel', default='UC9tj7V7QFAMRRzwPUvKNKEA')
    args = ap.parse_args()
    windows = args.window or [6, 24]

    g = YouTubeGrowthManager()
    g.authenticate()

    now = dt.datetime.now(BRT)
    recent = []
    for key, e in g.history.items():
        if not isinstance(e, dict):
            continue
        if e.get('status') != 'published' or not e.get('video_id'):
            continue
        pub = e.get('published_at')
        if not pub:
            continue
        try:
            t = parse_brt(pub)
        except Exception:
            continue
        age_h = (now - t).total_seconds() / 3600
        if 0 <= age_h <= RECENT_H:
            recent.append((age_h, t, e))

    recent.sort(key=lambda x: x[0])  # mais novo primeiro
    if not recent:
        print(f'Nenhum vídeo publicado nas últimas {RECENT_H}h.')
        return

    ids = [e['video_id'] for _, _, e in recent]
    # metrics: views, likes, comments, avgViewDuration, avgViewPercentage
    fields = ','.join([
        'videos(id)',
        'metrics(views,likes,comments,averageViewDuration,averageViewPercentage)',
    ])
    resp = g.analytics_service.reports().query(
        ids='channel==MINE',
        startDate=(now - dt.timedelta(hours=RECENT_H)).strftime('%Y-%m-%d'),
        endDate=now.strftime('%Y-%m-%d'),
        dimensions='video',
        filters='video==' + ','.join(ids),
        metrics='views,likes,comments,averageViewDuration,averageViewPercentage',
    ).execute()

    rows = {}
    cols = [c['name'] for c in resp['columnHeaders']]
    for r in resp.get('rows', []):
        d = dict(zip(cols, r))
        rows[d['video.id']] = d

    print(f'=== CHECK — {now.strftime("%Y-%m-%d %H:%M")} BRT | elegíveis: {len(recent)} ===')
    for age_h, t, e in recent:
        vid = e['video_id']
        m = rows.get(vid, {})
        views = int(m.get('views', 0) or 0)
        likes = int(m.get('likes', 0) or 0)
        comments = int(m.get('comments', 0) or 0)
        avd = float(m.get('averageViewDuration', 0) or 0)
        avp = float(m.get('averageViewPercentage', 0) or 0)
        due = [w for w in windows if age_h >= w]
        gate = 'PASS' if avp >= RETENTION_GATE else ('NA' if avp == 0 else 'FAIL')
        flag = ' '.join(f'{w}h✓' for w in due) if due else ''
        title = (e.get('title') or '')[:52]
        print(f'[{flag or "--"}] {age_h:5.1f}h  {gate:>4}  ret={avp:5.1f}%  '
              f'v={views:<5} l={likes:<3} c={comments:<3}  {vid}  {title}')

    fails = [vid for vid, m in rows.items()
             if float(m.get('averageViewPercentage', 0) or 0) and
             float(m.get('averageViewPercentage', 0)) < RETENTION_GATE]
    print(f'\nGate retenção >{RETENTION_GATE}%: '
          f'{len(rows)-len(fails)}/{len(rows)} PASS' +
          (f' | FAIL: {", ".join(fails)}' if fails else ''))
    if fails:
        print('Ação: analisar curve desses IDs antes de escalar/reativar guardados.')


if __name__ == '__main__':
    main()
