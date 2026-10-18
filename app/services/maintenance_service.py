from __future__ import annotations
from pathlib import Path
import shutil
import subprocess


class MaintenanceService:
    @staticmethod
    def _run(command, timeout=25):
        try:
            return subprocess.run(
                command, capture_output=True, text=True,
                timeout=timeout, check=False
            )
        except Exception as exc:
            class Result:
                returncode = 1
                stdout = ""
                stderr = str(exc)
            return Result()

    @classmethod
    def upgradable_packages(cls):
        result = cls._run(["apt", "list", "--upgradable"], 30)
        rows = []
        for line in result.stdout.splitlines():
            if not line or line.startswith("Listing"):
                continue
            name = line.split("/", 1)[0].strip()
            if name:
                rows.append(name)
        return rows

    @classmethod
    def broken_packages(cls):
        result = cls._run(["dpkg", "--audit"], 12)
        return [x for x in result.stdout.splitlines() if x.strip()]

    @staticmethod
    def directory_size(path: Path):
        total = 0
        try:
            for item in path.rglob("*"):
                try:
                    if item.is_file() and not item.is_symlink():
                        total += item.stat().st_size
                except OSError:
                    pass
        except OSError:
            pass
        return total

    @classmethod
    def cleanup_scan(cls):
        home = Path.home()
        apt_cache = Path("/var/cache/apt/archives")
        thumbs = home / ".cache/thumbnails"
        trash = home / ".local/share/Trash/files"
        return {
            "APT package cache": cls.directory_size(apt_cache),
            "Thumbnail cache": cls.directory_size(thumbs),
            "User trash": cls.directory_size(trash),
        }

    @staticmethod
    def human_size(value):
        units = ["B", "KB", "MB", "GB", "TB"]
        size = float(value)
        for unit in units:
            if size < 1024 or unit == units[-1]:
                return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
            size /= 1024
        return "0 B"

    @staticmethod
    def _clear_folder(folder: Path):
        removed = 0
        if not folder.exists():
            return removed
        for item in list(folder.iterdir()):
            try:
                if item.is_symlink():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                removed += 1
            except OSError:
                pass
        return removed

    @classmethod
    def cleanup_thumbnails(cls):
        return cls._clear_folder(Path.home() / ".cache/thumbnails")

    @classmethod
    def cleanup_trash(cls):
        files = Path.home() / ".local/share/Trash/files"
        info = Path.home() / ".local/share/Trash/info"
        return cls._clear_folder(files) + cls._clear_folder(info)

    @classmethod
    def user_cleanup(cls):
        return cls.cleanup_thumbnails() + cls.cleanup_trash()

    @staticmethod
    def apt_cleanup_command():
        return ["pkexec", "apt-get", "clean"]

    @staticmethod
    def update_command():
        return ["pkexec", "apt-get", "update"]

    @staticmethod
    def upgrade_command():
        return ["pkexec", "apt-get", "upgrade", "-y"]
