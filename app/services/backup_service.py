from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import shutil
import subprocess


class BackupService:
    BASE = Path.home() / ".local/share/initra/backups"
    MANAGED = {
        "Initra settings": Path.home() / ".config/initra/settings.json",
        "Autostart": Path.home() / ".config/autostart",
        "Git config": Path.home() / ".gitconfig",
        "Bash config": Path.home() / ".bashrc",
    }

    def __init__(self):
        self.BASE.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _run(command, timeout=8):
        try:
            return subprocess.run(
                command, capture_output=True, text=True,
                timeout=timeout, check=False
            )
        except Exception:
            return None

    def create_backup(self, reason="Manual backup"):
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        folder = self.BASE / stamp
        folder.mkdir(parents=True, exist_ok=False)

        manifest = {
            "created": datetime.now().isoformat(timespec="seconds"),
            "reason": reason,
            "files": [],
            "gsettings": {},
        }

        files_dir = folder / "files"
        files_dir.mkdir()

        for name, source in self.MANAGED.items():
            if not source.exists():
                continue
            target = files_dir / name.replace(" ", "_").lower()
            try:
                if source.is_dir():
                    shutil.copytree(source, target)
                    kind = "dir"
                else:
                    shutil.copy2(source, target)
                    kind = "file"
                manifest["files"].append({
                    "name": name,
                    "source": str(source),
                    "backup": str(target.relative_to(folder)),
                    "kind": kind,
                })
            except OSError:
                pass

        # Back up only the GNOME keys that Initra v1.4+ can change.
        keys = [
            ("org.gnome.desktop.interface", "enable-animations"),
            ("org.gnome.desktop.interface", "enable-hot-corners"),
            ("org.gnome.desktop.interface", "show-battery-percentage"),
            ("org.gnome.desktop.interface", "clock-show-weekday"),
        ]
        for schema, key in keys:
            result = self._run(["gsettings", "get", schema, key])
            if result and result.returncode == 0:
                manifest["gsettings"][f"{schema}|{key}"] = result.stdout.strip()

        (folder / "manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )
        return folder

    def list_backups(self):
        result = []
        if not self.BASE.exists():
            return result
        for folder in sorted(self.BASE.iterdir(), reverse=True):
            manifest_path = folder / "manifest.json"
            if not folder.is_dir() or not manifest_path.exists():
                continue
            try:
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            data["path"] = str(folder)
            data["id"] = folder.name
            result.append(data)
        return result

    def restore(self, backup_id):
        folder = self.BASE / backup_id
        manifest_path = folder / "manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError("Backup manifest was not found.")

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        restored = []

        for item in manifest.get("files", []):
            source = folder / item["backup"]
            target = Path(item["source"])
            if not source.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                if target.is_dir() and not target.is_symlink():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            if item["kind"] == "dir":
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)
            restored.append(item["name"])

        for token, value in manifest.get("gsettings", {}).items():
            try:
                schema, key = token.split("|", 1)
            except ValueError:
                continue
            self._run(["gsettings", "set", schema, key, value])

        return restored

    def delete(self, backup_id):
        folder = self.BASE / backup_id
        if folder.exists() and folder.is_dir():
            shutil.rmtree(folder)
            return True
        return False

    def latest(self):
        items = self.list_backups()
        return items[0] if items else None
