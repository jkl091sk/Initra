from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json
import uuid


class ProfileService:
    BASE = Path.home() / ".local/share/initra/profiles"

    BUILT_INS = {
        "Developer": {
            "description": "Development tools, Git, Python and build essentials.",
            "packages": ["git", "python3-pip", "build-essential", "cmake", "curl"],
            "services": [],
            "tweaks": {"animations": True, "hot_corners": False},
            "dotfiles": True,
        },
        "Essential": {
            "description": "A lightweight everyday Linux baseline.",
            "packages": ["curl", "wget", "htop", "vlc"],
            "services": [],
            "tweaks": {"animations": True, "hot_corners": True},
            "dotfiles": False,
        },
        "Gaming": {
            "description": "Gaming packages and performance utilities.",
            "packages": ["steam", "gamemode", "mangohud", "wine"],
            "services": [],
            "tweaks": {"animations": True, "hot_corners": False},
            "dotfiles": False,
        },
        "Creator": {
            "description": "Creative applications for graphics, audio and video.",
            "packages": ["gimp", "blender", "obs-studio", "audacity", "inkscape"],
            "services": [],
            "tweaks": {"animations": True, "hot_corners": False},
            "dotfiles": False,
        },
    }

    def __init__(self):
        self.BASE.mkdir(parents=True, exist_ok=True)

    def built_ins(self):
        result = []
        for name, data in self.BUILT_INS.items():
            item = dict(data)
            item.update({"id": f"builtin:{name}", "name": name, "builtin": True})
            result.append(item)
        return result

    def custom_profiles(self):
        rows = []
        for file in sorted(self.BASE.glob("*.json")):
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                data["builtin"] = False
                data["path"] = str(file)
                rows.append(data)
            except Exception:
                pass
        return rows

    def all_profiles(self):
        return self.built_ins() + self.custom_profiles()

    def get(self, profile_id):
        for item in self.all_profiles():
            if item["id"] == profile_id or item["name"] == profile_id:
                return item
        return None

    def save(self, data):
        profile_id = data.get("id")
        if not profile_id or str(profile_id).startswith("builtin:"):
            profile_id = str(uuid.uuid4())
        payload = {
            "id": profile_id,
            "name": data.get("name", "Custom profile").strip() or "Custom profile",
            "description": data.get("description", "").strip(),
            "packages": sorted(set(data.get("packages", []))),
            "services": sorted(set(data.get("services", []))),
            "tweaks": dict(data.get("tweaks", {})),
            "dotfiles": bool(data.get("dotfiles", False)),
            "created": data.get("created") or datetime.now().isoformat(timespec="seconds"),
            "updated": datetime.now().isoformat(timespec="seconds"),
        }
        (self.BASE / f"{profile_id}.json").write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )
        return payload

    def duplicate(self, profile):
        clone = dict(profile)
        clone.pop("path", None)
        clone["id"] = ""
        clone["name"] = f"{profile['name']} Copy"
        clone["created"] = None
        return self.save(clone)

    def delete(self, profile_id):
        target = self.BASE / f"{profile_id}.json"
        if target.exists():
            target.unlink()
            return True
        return False
