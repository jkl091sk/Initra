from __future__ import annotations

from pathlib import Path
import shutil
import subprocess


class SoftwareService:
    APT_APPS = {
        "Development": {
            "git": "Distributed version control",
            "code": "Visual Studio Code (when repository is configured)",
            "python3-pip": "Python package installer",
            "build-essential": "Compiler and build toolchain",
            "cmake": "Cross-platform build system",
            "nodejs": "JavaScript runtime",
        },
        "Gaming": {
            "steam": "Steam game platform",
            "gamemode": "Gaming performance daemon",
            "mangohud": "Vulkan/OpenGL performance overlay",
            "wine": "Windows compatibility layer",
        },
        "Creative": {
            "gimp": "Image editor",
            "blender": "3D creation suite",
            "obs-studio": "Recording and streaming",
            "audacity": "Audio editor",
            "inkscape": "Vector graphics editor",
            "kdenlive": "Video editor",
        },
        "Internet": {
            "thunderbird": "Email client",
            "filezilla": "FTP/SFTP client",
            "transmission-gtk": "BitTorrent client",
        },
        "Utilities": {
            "vlc": "Media player",
            "htop": "Interactive process viewer",
            "neofetch": "System information utility",
            "gnome-tweaks": "GNOME customization utility",
            "curl": "Command-line data transfer",
            "wget": "Network downloader",
        },
    }

    FLATPAK_APPS = {
        "Development": {
            "com.visualstudio.code": ("Visual Studio Code", "Code editor"),
            "com.getpostman.Postman": ("Postman", "API development client"),
        },
        "Gaming": {
            "com.valvesoftware.Steam": ("Steam", "Game platform"),
            "net.lutris.Lutris": ("Lutris", "Open gaming platform"),
            "com.heroicgameslauncher.hgl": ("Heroic Games Launcher", "Epic/GOG launcher"),
        },
        "Creative": {
            "org.gimp.GIMP": ("GIMP", "Image editor"),
            "org.blender.Blender": ("Blender", "3D creation suite"),
            "com.obsproject.Studio": ("OBS Studio", "Recording and streaming"),
            "org.kde.kdenlive": ("Kdenlive", "Video editor"),
        },
        "Internet": {
            "org.mozilla.firefox": ("Firefox", "Web browser"),
            "org.telegram.desktop": ("Telegram Desktop", "Messaging client"),
        },
        "Utilities": {
            "org.videolan.VLC": ("VLC", "Media player"),
            "com.github.tchx84.Flatseal": ("Flatseal", "Flatpak permissions manager"),
        },
    }

    @staticmethod
    def _run(command, timeout=15):
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

    @staticmethod
    def has_flatpak():
        return shutil.which("flatpak") is not None

    @classmethod
    def apt_installed(cls, package):
        result = cls._run(["dpkg-query", "-W", "-f=${Status}", package], 4)
        return result.stdout.strip() == "install ok installed"

    @classmethod
    def flatpak_installed(cls, app_id):
        if not cls.has_flatpak():
            return False
        result = cls._run(["flatpak", "info", app_id], 5)
        return result.returncode == 0

    @staticmethod
    def apt_install_command(package):
        return ["pkexec", "apt-get", "install", "-y", package]

    @staticmethod
    def apt_remove_command(package):
        return ["pkexec", "apt-get", "remove", "-y", package]

    @staticmethod
    def flatpak_install_command(app_id):
        return ["flatpak", "install", "-y", "flathub", app_id]

    @staticmethod
    def flatpak_remove_command(app_id):
        return ["flatpak", "uninstall", "-y", app_id]

    @staticmethod
    def install_flatpak_command():
        return ["pkexec", "apt-get", "install", "-y", "flatpak"]

    @staticmethod
    def add_flathub_command():
        return [
            "flatpak", "remote-add", "--if-not-exists", "flathub",
            "https://flathub.org/repo/flathub.flatpakrepo"
        ]

    @classmethod
    def flatpak_remotes(cls):
        if not cls.has_flatpak():
            return []
        result = cls._run(["flatpak", "remotes", "--columns=name,url"], 8)
        rows = []
        for line in result.stdout.splitlines():
            parts = line.split("\t", 1)
            if parts and parts[0].strip():
                rows.append((parts[0].strip(), parts[1].strip() if len(parts) > 1 else ""))
        return rows

    @staticmethod
    def apt_sources():
        files = [Path("/etc/apt/sources.list")]
        source_dir = Path("/etc/apt/sources.list.d")
        if source_dir.exists():
            files.extend(sorted(source_dir.glob("*.list")))
            files.extend(sorted(source_dir.glob("*.sources")))
        rows = []
        for file in files:
            if not file.exists():
                continue
            try:
                content = file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            enabled = []
            for line in content.splitlines():
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    enabled.append(stripped)
            rows.append((str(file), enabled))
        return rows
