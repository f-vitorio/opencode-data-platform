#!/usr/bin/env python3
"""
Sincroniza history.json com o estado real no YouTube (fonte de verdade).

Para cada entrada do history com video_id:
  - video_id inexistente no canal      -> status = deleted
  - privacyStatus = public             -> status = published, published_at (BRT)
  - private + publishAt                -> status = scheduled,  scheduled_at (BRT)
  - private sem publishAt              -> status = uploaded

Uso:
  python3 sync_history.py            # dry-run (mostra divergências, não grava)
  python3 sync_history.py --apply    # grava o history.json
  python3 sync_history.py --apply --backup   # grava com backup automático

Somente campos de estado são alterados. Título/descrição/hashtags/links
nunca são modificados aqui (para isso existe fix_metadata_seo.py).
"""
import argparse
import datetime as dt
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from youtube_growth import YouTubeGrowthManager

BRT = dt.timezone(dt.timedelta(hours=-3))
HISTORY = Path(__file__).parent / "history.json"


def to_brt(iso_z: str):
    """'2026-09-28T15:00:00Z' -> '2026-09-28T12:00:00' (naive BRT)."""
    d = dt.datetime.fromisoformat(iso_z.replace("Z", "+00:00")).astimezone(BRT)
    return d.replace(tzinfo=None).isoformat(timespec="seconds")


def fetch_live(manager: YouTubeGrowthManager, ids):
    """videos.list em lotes de 50 -> {video_id: status_dict}"""
    live = {}
    for i in range(0, len(ids), 50):
        resp = manager.youtube_service.videos().list(
            part="status", id=",".join(ids[i:i + 50])
        ).execute()
        for item in resp.get("items", []):
            live[item["id"]] = item["status"]
    return live


def plan_changes(history, live):
    changes = []
    for stem, entry in history.items():
        if not isinstance(entry, dict) or not entry.get("video_id"):
            continue
        vid = entry["video_id"]
        cur = entry.get("status")
        st = live.get(vid)

        if st is None:
            new_status, published_at, scheduled_at, reason = (
                "deleted", None, None, "video_id não existe no canal")
        elif st.get("privacyStatus") == "public":
            new_status = "published"
            reason = "privacyStatus=public"
            # publishedAt não vem em part=status; usa o do snippet se disponível
            published_at = entry.get("published_at")
            scheduled_at = None
        elif st.get("publishAt"):
            new_status = "scheduled"
            published_at = None
            scheduled_at = to_brt(st["publishAt"])
            reason = "private + publishAt"
        else:
            new_status, published_at, scheduled_at = "uploaded", None, None
            reason = "private sem publishAt"

        if new_status == cur:
            continue

        # preserva published_at conhecido quando já era published
        if new_status == "published" and not published_at:
            published_at = entry.get("published_at")

        changes.append(dict(
            stem=stem, video_id=vid, current=cur, new=new_status,
            reason=reason, published_at=published_at,
            scheduled_at=scheduled_at, old_scheduled=entry.get("scheduled_at"),
        ))
    return changes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="grava no history.json (default: dry-run)")
    ap.add_argument("--backup", action="store_true",
                    help="cria backup antes de gravar")
    args = ap.parse_args()

    manager = YouTubeGrowthManager()
    if not manager.authenticate():
        print("[Sync] Falha na autenticação")
        return 1

    history = manager.history
    ids = [e["video_id"] for e in history.values()
           if isinstance(e, dict) and e.get("video_id")]
    print(f"[Sync] {len(ids)} entries com video_id")

    live = fetch_live(manager, ids)
    print(f"[Sync] {len(live)} encontrados no YouTube | "
          f"{len(ids) - len(live)} ausentes")

    changes = plan_changes(history, live)

    # publishedAt exato vem do snippet (part=status não o retorna)
    public_new = [c for c in changes if c["new"] == "published"]
    if public_new:
        pub_ids = [c["video_id"] for c in public_new]
        for i in range(0, len(pub_ids), 50):
            resp = manager.youtube_service.videos().list(
                part="snippet", id=",".join(pub_ids[i:i + 50])
            ).execute()
            by_id = {it["id"]: it["snippet"].get("publishedAt")
                     for it in resp.get("items", [])}
            for c in public_new:
                iso = by_id.get(c["video_id"])
                if iso:
                    c["published_at"] = to_brt(iso)

    if not changes:
        print("[Sync] history.json já está sincronizado. Nada a fazer.")
        return 0

    print(f"\n=== DIVERGÊNCIAS: {len(changes)} ===")
    for c in changes:
        print(f"  {c['stem']}")
        print(f"    {c['video_id']}  {c['current']} -> {c['new']}  ({c['reason']})")
        if c["new"] == "published":
            print(f"    published_at: {c['published_at']}")
        if c["new"] == "scheduled":
            print(f"    scheduled_at: {c['old_scheduled']} -> {c['scheduled_at']}")
        if c["new"] == "deleted":
            print(f"    status local: {c['current']} -> deleted")

    if not args.apply:
        print("\n[Sync] DRY-RUN — nada foi alterado. Rode com --apply para gravar.")
        return 0

    if args.backup:
        ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        bak = HISTORY.with_suffix(f".json.bak-{ts}-pre-sync")
        shutil.copy2(HISTORY, bak)
        print(f"[Sync] backup: {bak.name}")

    for c in changes:
        entry = history[c["stem"]]
        entry["status"] = c["new"]
        if c["new"] == "published":
            if c["published_at"]:
                entry["published_at"] = c["published_at"]
            entry.pop("scheduled_at", None)
            entry["privacy_status"] = "public"
        elif c["new"] == "scheduled":
            if c["scheduled_at"]:
                entry["scheduled_at"] = c["scheduled_at"]
            entry.pop("published_at", None)
            entry["privacy_status"] = "private"

    manager.save_history()
    print(f"[Sync] aplicadas: {len(changes)} | history salvo")

    # resumo final
    from collections import Counter
    final = Counter(e.get("status") for e in history.values() if isinstance(e, dict))
    print(f"[Sync] status final: {dict(final)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
