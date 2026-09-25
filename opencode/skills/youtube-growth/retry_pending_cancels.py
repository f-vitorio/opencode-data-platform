#!/usr/bin/env python3
"""Retry pending YouTube schedule-cancel after daily quota reset.

Reads pending_cancels.json, cancels each old video, removes done items.
Also optionally backfills UTM description on replacement videos.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SKILL_DIR))

PENDING = SKILL_DIR / "pending_cancels.json"
LOG = Path("/tmp/youtube-pending-cancels.log")


def log(msg: str) -> None:
    line = f"{datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line, flush=True)
    with LOG.open("a") as f:
        f.write(line + "\n")


def main() -> int:
    if not PENDING.exists():
        log("no pending_cancels.json — nothing to do")
        return 0

    data = json.loads(PENDING.read_text())
    items = data.get("items") or []
    if not items:
        log("pending list empty — nothing to do")
        return 0

    from youtube_growth import YouTubeGrowthManager

    mgr = YouTubeGrowthManager()
    mgr.authenticate()
    log(f"starting cancel retry for {len(items)} items")

    remaining = []
    for item in items:
        old_id = item["old_video_id"]
        old_key = item.get("old_key")
        new_id = item.get("new_video_id")
        try:
            ok = mgr.cancel_scheduled_video(old_id)
        except Exception as e:
            log(f"ERROR cancel {old_id} ({old_key}): {e}")
            remaining.append(item)
            continue

        if ok:
            log(f"OK cancel {old_id} ({old_key}) replaced_by={new_id}")
            # refresh history status
            if old_key and old_key in mgr.history:
                entry = mgr.history[old_key]
                entry["status"] = "uploaded"
                entry["scheduled_at"] = None
                entry["privacy_status"] = "private"
                entry["pending_cancel_reason"] = "cancelled"
                mgr.save_history()
        else:
            log(f"FAIL cancel {old_id} ({old_key}) — still in quota or not found")
            remaining.append(item)

    data["items"] = remaining
    data["last_retry_at"] = datetime.now().isoformat()
    if not remaining:
        data["status"] = "all_cancelled"
    else:
        data["status"] = "partial"
    PENDING.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    log(f"done. remaining={len(remaining)}")
    return 0 if not remaining else 2


if __name__ == "__main__":
    raise SystemExit(main())
