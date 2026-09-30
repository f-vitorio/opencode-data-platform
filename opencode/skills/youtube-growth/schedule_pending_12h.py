#!/usr/bin/env python3
"""
Agenda os vídeos 'uploaded' (guardados) da leva 12:00 BRT (15:00Z).

Regra: 1 vídeo/dia às 15:00Z (= 12:00 BRT), na ordem de inserção do
history.json, ocupando o primeiro horário LIVRE a partir do dia base.
Datas já ocupadas pela leva (inclusive as antigas) são puladas, então a
execução é idempotente: rodar de novo só agenda o que falta.

Uso:
  python3 schedule_pending_12h.py           # agenda o que falta
  python3 schedule_pending_12h.py --dry     # só mostra o plano
"""
import sys
import datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from youtube_growth import YouTubeGrowthManager

FIRST_DAY = dt.date(2026, 9, 27)   # primeiro dia livre da leva (12:00 BRT)
UTC_TIME = dt.time(15, 0)          # 15:00Z = 12:00 BRT

# Vídeos que o YouTube recusa agendar (HttpError 400 invalidPublishAt em qualquer data).
# Ficam privados; resolver com re-upload ou publicação manual.
SKIP = {'qNh9Rt7uqIY'}


def taken_days(g):
    """Datas já ocupadas por um vídeo da leva das 12:00 BRT."""
    days = set()
    for v in g.history.values():
        if isinstance(v, dict) and v.get('status') == 'scheduled':
            sa = v.get('scheduled_at') or ''
            if sa.endswith('T15:00:00'):
                days.add(sa[:10])
    return days


def free_slots(g, count):
    """Primeiros `count` dias livres >= FIRST_DAY (datas passadas são ignoradas)."""
    taken = taken_days(g)
    day = max(FIRST_DAY, dt.date.today() + dt.timedelta(days=1))
    slots = []
    while len(slots) < count:
        if day.isoformat() not in taken:
            slots.append(dt.datetime.combine(day, UTC_TIME))
        day += dt.timedelta(days=1)
    return slots


def main():
    dry = '--dry' in sys.argv
    g = YouTubeGrowthManager()

    pending = [(k, v) for k, v in g.history.items()
               if isinstance(v, dict) and v.get('status') == 'uploaded'
               and v.get('video_id') and v['video_id'] not in SKIP]
    skipped = [k for k, v in g.history.items() if isinstance(v, dict)
               and v.get('status') == 'uploaded' and v.get('video_id') in SKIP]

    if not pending:
        print('[YouTube] Nada pendente: todos da leva já estão agendados.')
        return 0

    slots = free_slots(g, len(pending))
    print(f'[YouTube] Pendentes: {len(pending)} | leva 12:00 BRT a partir de '
          f'{slots[0].strftime("%d/%m/%Y")}')
    for k in skipped:
        print(f'[YouTube] IGNORADO (publishAt recusado pela API): {k}')
    ok = fail = 0
    for (k, v), when in zip(pending, slots):
        print(f'  {when.strftime("%d/%m %H:%MZ")} (=12:00 BRT)  {v["video_id"]}  {k}')
        if dry:
            continue
        if g.schedule_existing_publish(v['video_id'], when):
            ok += 1
        else:
            fail += 1
            print('[YouTube] Interrompendo: falha provável de cota. Rode novamente após o reset.')
            break

    if dry:
        print(f'[YouTube] Dry-run: {len(pending)} para agendar.')
    else:
        print(f'[YouTube] Retomada: ok={ok} fail={fail} restantes={len(pending) - ok}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
