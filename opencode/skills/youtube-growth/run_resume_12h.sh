#!/usr/bin/env bash
# Espera a cota da YouTube Data API voltar e retoma o agendamento da leva 12:00 BRT.
# Roda em background (nohup); termina quando os 38 estiverem agendados e verificados.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$DIR/resume_12h.log"
cd "$DIR" || exit 1

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG"; }

log "LOOP INICIADO (esperando reset de cota ~04:00 BRT de 25/09)"

while true; do
  OUT="$(python3 schedule_pending_12h.py 2>&1)"
  echo "$OUT" >> "$LOG"

  if echo "$OUT" | grep -q "Nada pendente"; then
    log "TODOS AGENDADOS. Verificando publishAt no YouTube..."
    VER="$(python3 - <<'PY' 2>&1
import sys
sys.path.insert(0, '.')
from youtube_growth import YouTubeGrowthManager
g = YouTubeGrowthManager(); g.authenticate()
ids = [v['video_id'] for v in g.history.values()
       if isinstance(v, dict) and v.get('video_id') and
       (v.get('status') == 'scheduled' and (v.get('scheduled_at') or '').endswith('T15:00:00'))]
ok = bad = 0
for i in range(0, len(ids), 50):
    r = g.youtube_service.videos().list(part='status', id=','.join(ids[i:i+50])).execute()
    found = {it['id']: it['status'] for it in r.get('items', [])}
    for vid in ids[i:i+50]:
        s = found.get(vid, {})
        pa = s.get('publishAt', '')
        if s.get('privacyStatus') == 'private' and pa.startswith('2026') and 'T15:00:00' in pa:
            ok += 1
        else:
            bad += 1
            print(f'  DIVERGENTE {vid} priv={s.get("privacyStatus")} publishAt={pa}')
print(f'VERIFICACAO: ok={ok} divergentes={bad} de {len(ids)}')
PY
)"
    echo "$VER" >> "$LOG"
    if echo "$VER" | grep -q "divergentes=0"; then
      log "CONCLUIDO E VERIFICADO COM SUCESSO"
      exit 0
    fi
    log "HA DIVERGENCIAS — repetindo em 1h"
    sleep 3600
    continue
  fi

  if echo "$OUT" | grep -q "restantes=0"; then
    log "agendamento ok, mas:Nada pendente nao detectado — nova tentativa em 10min"
    sleep 600
    continue
  fi

  # cota ainda estourada (fail) → tenta de novo em 30min
  log "ainda sem cota ou falha — nova tentativa em 30min"
  sleep 1800
done
