from __future__ import annotations
import shutil
import subprocess

class NotificationService:
    @staticmethod
    def send(title: str, message: str) -> bool:
        if not shutil.which("notify-send"):
            return False
        try:
            subprocess.Popen(
                ["notify-send", "--app-name=Initra", title, message],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            return True
        except Exception:
            return False
