from __future__ import annotations
from pathlib import Path
import shutil
import subprocess


class MaintenanceService:
    def __init__(self, distro=None):
        self.distro = distro

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

    def _manager(self):
        if self.distro is not None:
            return self.distro.info.get("package_manager", "unknown")
        if shutil.which("apt") or shutil.which("apt-get"):
            return "apt"
        if shutil.which("dnf"):
            return "dnf"
        if shutil.which("pacman"):
            return "pacman"
        if shutil.which("zypper"):
            return "zypper"
        return "unknown"

    def upgradable_packages(self):
        manager = self._manager()
        if manager == "apt":
            result = self._run(["apt", "list", "--upgradable"], 30)
            return [
                line.split("/", 1)[0].strip()
                for line in result.stdout.splitlines()
                if line.strip() and not line.startswith("Listing") and "/" in line
            ]
        if manager == "dnf":
            result = self._run(["dnf", "check-update", "--quiet"], 30)
            rows = []
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 3 and not line.startswith(("Last metadata", "Obsoleting")):
                    rows.append(parts[0])
            return rows
        if manager == "pacman":
            if shutil.which("checkupdates"):
                result = self._run(["checkupdates"], 30)
                return [line.split()[0] for line in result.stdout.splitlines() if line.split()]
            return []
        if manager == "zypper":
            result = self._run(["zypper", "--non-interactive", "list-updates"], 30)
            rows = []
            for line in result.stdout.splitlines():
                parts = [part.strip() for part in line.split("|")]
                if len(parts) >= 3 and parts[0].lower() in {"v", ""} and parts[2] and parts[2] != "Name":
                    rows.append(parts[2])
            return rows
        return []

    def broken_packages(self):
        manager = self._manager()
        if manager == "apt":
            result = self._run(["dpkg", "--audit"], 12)
            return [x for x in result.stdout.splitlines() if x.strip()]
        if manager == "pacman":
            result = self._run(["pacman", "-Qk"], 25)
            return [x for x in result.stdout.splitlines() if " 0 missing files" not in x and "missing file" in x.lower()]
        return []

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

    def package_cache_path(self):
        manager = self._manager()
        return {
            "apt": Path("/var/cache/apt/archives"),
            "dnf": Path("/var/cache/dnf"),
            "pacman": Path("/var/cache/pacman/pkg"),
            "zypper": Path("/var/cache/zypp"),
        }.get(manager)

    def cleanup_scan(self):
        home = Path.home()
        cache = self.package_cache_path()
        thumbs = home / ".cache/thumbnails"
        trash = home / ".local/share/Trash/files"
        return {
            "Package cache": self.directory_size(cache) if cache else 0,
            "Thumbnail cache": self.directory_size(thumbs),
            "User trash": self.directory_size(trash),
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

    def update_command(self):
        return self.distro.update_command() if self.distro is not None else None

    def upgrade_command(self):
        return self.distro.upgrade_command() if self.distro is not None else None

    def cleanup_command(self):
        return self.distro.cleanup_command() if self.distro is not None else None
