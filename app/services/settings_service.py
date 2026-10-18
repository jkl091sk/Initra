import json
from pathlib import Path

class SettingsService:
    def __init__(self):
        self.path = Path.home() / ".config/initra/settings.json"
        self.defaults = {
            "confirm_apply": True,
            "show_system_snapshot": True,
            "remember_profile": True,
            "profile": "Developer",
            "animations": True,
            "notifications": True,
            "confirm_cleanup": True,
            "auto_check_updates": True,
            "history_days": 30,
            "first_run_complete": False,
            "wizard_profile": "Developer",
        }

    def load(self):
        if not self.path.exists():
            return dict(self.defaults)
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return {**self.defaults, **data}
        except Exception:
            return dict(self.defaults)

    def save(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
