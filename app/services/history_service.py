from __future__ import annotations
from datetime import datetime, timedelta
from pathlib import Path

class HistoryService:
    @staticmethod
    def prune(path: Path, days: int) -> None:
        if days <= 0 or not path.exists():
            return
        cutoff = datetime.now() - timedelta(days=days)
        kept = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                stamp = line.split("]", 1)[0].lstrip("[")
                when = datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S")
                if when >= cutoff:
                    kept.append(line)
            except Exception:
                kept.append(line)
        path.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")
