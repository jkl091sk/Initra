from __future__ import annotations

from pathlib import Path
import os
import platform
import shutil
import subprocess


class DistroService:
    FAMILY_MAP = {
        "ubuntu": "debian", "linuxmint": "debian", "pop": "debian",
        "elementary": "debian", "zorin": "debian", "kali": "debian",
        "debian": "debian",
        "fedora": "fedora", "rhel": "fedora", "centos": "fedora",
        "rocky": "fedora", "almalinux": "fedora", "nobara": "fedora",
        "arch": "arch", "manjaro": "arch", "endeavouros": "arch",
        "garuda": "arch",
        "opensuse-tumbleweed": "suse", "opensuse-leap": "suse",
        "opensuse": "suse", "sles": "suse",
    }

    PACKAGE_ALIASES = {
        "build-essential": {
            "debian": ["build-essential"],
            "fedora": ["gcc", "gcc-c++", "make"],
            "arch": ["base-devel"],
            "suse": ["patterns-devel-base-devel_basis"],
        },
        "python3-pip": {"debian": ["python3-pip"], "fedora": ["python3-pip"],
                        "arch": ["python-pip"], "suse": ["python3-pip"]},
        "steam": {"debian": ["steam"], "fedora": ["steam"],
                  "arch": ["steam"], "suse": ["steam"]},
        "gamemode": {"debian": ["gamemode"], "fedora": ["gamemode"],
                     "arch": ["gamemode"], "suse": ["gamemode"]},
        "mangohud": {"debian": ["mangohud"], "fedora": ["mangohud"],
                     "arch": ["mangohud"], "suse": ["MangoHud"]},
        "wine": {"debian": ["wine"], "fedora": ["wine"],
                 "arch": ["wine"], "suse": ["wine"]},
        "obs-studio": {"debian": ["obs-studio"], "fedora": ["obs-studio"],
                       "arch": ["obs-studio"], "suse": ["obs-studio"]},
    }

    def __init__(self):
        self.info = self.detect()

    @staticmethod
    def _parse_os_release():
        data = {}
        path = Path("/etc/os-release")
        if not path.exists():
            return data
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if "=" not in raw or raw.lstrip().startswith("#"):
                continue
            key, value = raw.split("=", 1)
            data[key] = value.strip().strip('"').strip("'")
        return data

    @classmethod
    def detect(cls):
        data = cls._parse_os_release()
        distro_id = data.get("ID", "unknown").lower()
        like = data.get("ID_LIKE", "").lower().split()
        family = cls.FAMILY_MAP.get(distro_id)
        if not family:
            for item in like:
                family = cls.FAMILY_MAP.get(item)
                if family:
                    break
        managers = []
        for manager in ("apt-get", "dnf", "pacman", "zypper"):
            if shutil.which(manager):
                managers.append(manager)
        if family == "debian" and "apt-get" in managers:
            package_manager = "apt"
        elif family == "fedora" and "dnf" in managers:
            package_manager = "dnf"
        elif family == "arch" and "pacman" in managers:
            package_manager = "pacman"
        elif family == "suse" and "zypper" in managers:
            package_manager = "zypper"
        elif managers:
            package_manager = {"apt-get": "apt"}.get(managers[0], managers[0])
        else:
            package_manager = "unknown"

        desktop = os.environ.get("XDG_CURRENT_DESKTOP") or os.environ.get("DESKTOP_SESSION") or "Unknown"
        return {
            "id": distro_id,
            "name": data.get("NAME", distro_id.title() if distro_id != "unknown" else "Unknown Linux"),
            "pretty_name": data.get("PRETTY_NAME", data.get("NAME", "Unknown Linux")),
            "version": data.get("VERSION_ID", ""),
            "codename": data.get("VERSION_CODENAME", data.get("UBUNTU_CODENAME", "")),
            "id_like": like,
            "family": family or "unknown",
            "package_manager": package_manager,
            "architecture": platform.machine(),
            "kernel": platform.release(),
            "desktop": desktop,
            "session": os.environ.get("XDG_SESSION_TYPE", "unknown"),
        }

    def supported(self):
        return self.info["package_manager"] in {"apt", "dnf", "pacman", "zypper"}

    def translate_packages(self, packages):
        family = self.info["family"]
        output = []
        unsupported = []
        for package in packages:
            aliases = self.PACKAGE_ALIASES.get(package)
            if aliases and family in aliases:
                output.extend(aliases[family])
            elif aliases and family not in aliases:
                unsupported.append(package)
            else:
                output.append(package)
        # stable unique
        return list(dict.fromkeys(output)), unsupported

    def update_command(self):
        return {
            "apt": ["pkexec", "apt-get", "update"],
            "dnf": ["pkexec", "dnf", "makecache"],
            "pacman": ["pkexec", "pacman", "-Syu", "--noconfirm"],
            "zypper": ["pkexec", "zypper", "--non-interactive", "refresh"],
        }.get(self.info["package_manager"])

    def upgrade_command(self):
        return {
            "apt": ["pkexec", "apt-get", "upgrade", "-y"],
            "dnf": ["pkexec", "dnf", "upgrade", "-y"],
            "pacman": ["pkexec", "pacman", "-Syu", "--noconfirm"],
            "zypper": ["pkexec", "zypper", "--non-interactive", "update"],
        }.get(self.info["package_manager"])

    def install_command(self, packages):
        packages, unsupported = self.translate_packages(packages)
        if not packages:
            return None, unsupported
        manager = self.info["package_manager"]
        cmd = {
            "apt": ["pkexec", "apt-get", "install", "-y", *packages],
            "dnf": ["pkexec", "dnf", "install", "-y", *packages],
            "pacman": ["pkexec", "pacman", "-S", "--needed", "--noconfirm", *packages],
            "zypper": ["pkexec", "zypper", "--non-interactive", "install", *packages],
        }.get(manager)
        return cmd, unsupported

    def remove_command(self, packages):
        packages, unsupported = self.translate_packages(packages)
        manager = self.info["package_manager"]
        cmd = {
            "apt": ["pkexec", "apt-get", "remove", "-y", *packages],
            "dnf": ["pkexec", "dnf", "remove", "-y", *packages],
            "pacman": ["pkexec", "pacman", "-Rns", "--noconfirm", *packages],
            "zypper": ["pkexec", "zypper", "--non-interactive", "remove", *packages],
        }.get(manager) if packages else None
        return cmd, unsupported

    def cleanup_command(self):
        return {
            "apt": ["pkexec", "apt-get", "autoremove", "-y"],
            "dnf": ["pkexec", "dnf", "autoremove", "-y"],
            "pacman": ["pkexec", "pacman", "-Sc", "--noconfirm"],
            "zypper": ["pkexec", "zypper", "--non-interactive", "clean", "--all"],
        }.get(self.info["package_manager"])

    def installed(self, package):
        packages, _ = self.translate_packages([package])
        if not packages:
            return False
        package = packages[0]
        manager = self.info["package_manager"]
        commands = {
            "apt": ["dpkg-query", "-W", "-f=${Status}", package],
            "dnf": ["rpm", "-q", package],
            "pacman": ["pacman", "-Q", package],
            "zypper": ["rpm", "-q", package],
        }
        cmd = commands.get(manager)
        if not cmd:
            return False
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            return r.returncode == 0 and ("install ok installed" in r.stdout if manager == "apt" else True)
        except Exception:
            return False

    def repo_paths(self):
        family = self.info["family"]
        if family == "debian":
            return ["/etc/apt/sources.list", "/etc/apt/sources.list.d"]
        if family == "fedora":
            return ["/etc/yum.repos.d"]
        if family == "arch":
            return ["/etc/pacman.conf", "/etc/pacman.d"]
        if family == "suse":
            return ["/etc/zypp/repos.d"]
        return []

    def compatibility_notes(self):
        notes = []
        if not self.supported():
            notes.append("Package management is not yet supported for this distribution.")
        if "GNOME" not in self.info["desktop"].upper():
            notes.append("GNOME Tweaks are hidden/limited because GNOME was not detected.")
        if self.info["family"] != "debian":
            notes.append("Some legacy v1.x APT-only diagnostics are disabled in compatibility mode.")
        return notes
