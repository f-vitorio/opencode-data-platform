#!/usr/bin/env python3
"""
Retoma o agendamento dos vídeos 'uploaded' (guardados) da leva 12:00 BRT.

Regra: 1 vídeo/dia a partir de 2026-09-25, sempre 15:00Z (= 12:00 BRT),
na ordem original do history.json (índice fixo = data fixa), para que uma
interrupção (ex.: cota estourada) não desloque as datas dos já agendados.

Uso:
  python3 schedule_pending_12h.py           # agenda o que falta
  python3 schedule_pending_12h.py --dry     # só mostra o plano
"""
import sys
import datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from youtube_growth import YouTubeGrowthManager

BASE_DATE = dt.date(2026, 9, 25)   # primeiro dia da leva
UTC_TIME = dt.time(15, 0)          # 15:00Z = 12:00 BRT


def main():
    dry = '--dry' in sys.argv
    g = YouTubeGrowthManager()

    def in_batch(v):
        if not isinstance(v, dict) or not v.get('video_id'):
            return False
        if v.get('status') == 'uploaded':
            return True
        # já agendados nesta mesma leva (15:00Z = 12:00 BRT; lote antigo é 21:00Z)
        sa = v.get('scheduled_at') or ''
        return v.get('status') == 'scheduled' and sa.endswith('T15:00:00')

    # lote = ordem de inserção do history.json (mesma ordem dos 38 originais)
    batch = [(k, v) for k, v in g.history.items() if in_batch(v)]
    pending = [(i, k, v) for i, (k, v) in enumerate(batch) if v.get('status') == 'uploaded']

    if not pending:
        print('[YouTube] Nada pendente: todos da leva já estão agendados.')
        return 0

    print(f'[YouTube] Pendentes: {len(pending)} de {len(batch)} no lote')
    ok = fail = 0
    for idx, k, v in pending:
        day = BASE_DATE + dt.timedelta(days=idx)
        when = dt.datetime.combine(day, UTC_TIME)
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
