from __future__ import annotations

from pathlib import Path
import configparser
import os
import shutil
import subprocess


class SystemToolsService:
    @staticmethod
    def _run(command, timeout=12):
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

    # ---------- GNOME tweaks ----------
    @classmethod
    def gsettings_available(cls):
        return shutil.which("gsettings") is not None

    @classmethod
    def schema_exists(cls, schema):
        if not cls.gsettings_available():
            return False
        result = cls._run(["gsettings", "list-schemas"], 5)
        return schema in result.stdout.splitlines()

    @classmethod
    def key_exists(cls, schema, key):
        if not cls.schema_exists(schema):
            return False
        result = cls._run(["gsettings", "list-keys", schema], 5)
        return key in result.stdout.splitlines()

    @classmethod
    def get_setting(cls, schema, key):
        if not cls.key_exists(schema, key):
            return None
        result = cls._run(["gsettings", "get", schema, key], 5)
        return result.stdout.strip() if result.returncode == 0 else None

    @classmethod
    def set_setting(cls, schema, key, value):
        if not cls.key_exists(schema, key):
            return False, f"{schema}:{key} is not available on this desktop."
        result = cls._run(["gsettings", "set", schema, key, value], 5)
        return result.returncode == 0, (result.stderr.strip() or result.stdout.strip())

    # ---------- startup apps ----------
    @staticmethod
    def startup_dirs():
        return [
            (Path.home() / ".config/autostart", True),
            (Path("/etc/xdg/autostart"), False),
        ]

    @classmethod
    def startup_entries(cls):
        entries = []
        seen = set()
        for directory, user_owned in cls.startup_dirs():
            if not directory.exists():
                continue
            for file in sorted(directory.glob("*.desktop")):
                if file.name in seen:
                    continue
                seen.add(file.name)
                parser = configparser.ConfigParser(interpolation=None, strict=False)
                try:
                    parser.read(file, encoding="utf-8")
                    sec = parser["Desktop Entry"]
                except Exception:
                    continue
                entries.append({
                    "file": file,
                    "name": sec.get("Name", file.stem),
                    "exec": sec.get("Exec", ""),
                    "hidden": sec.get("Hidden", "false").lower() == "true",
                    "user_owned": user_owned,
                })
        return entries

    @staticmethod
    def _write_desktop(path, name, command, hidden=False):
        path.parent.mkdir(parents=True, exist_ok=True)
        content = (
            "[Desktop Entry]\n"
            "Type=Application\n"
            f"Name={name}\n"
            f"Exec={command}\n"
            f"Hidden={'true' if hidden else 'false'}\n"
            "X-GNOME-Autostart-enabled=true\n"
        )
        path.write_text(content, encoding="utf-8")

    @classmethod
    def set_startup_enabled(cls, entry, enabled):
        user_dir = Path.home() / ".config/autostart"
        target = user_dir / entry["file"].name
        if entry["user_owned"]:
            try:
                parser = configparser.ConfigParser(interpolation=None, strict=False)
                parser.optionxform = str
                parser.read(entry["file"], encoding="utf-8")
                if "Desktop Entry" not in parser:
                    parser["Desktop Entry"] = {}
                parser["Desktop Entry"]["Hidden"] = "false" if enabled else "true"
                with entry["file"].open("w", encoding="utf-8") as f:
                    parser.write(f, space_around_delimiters=False)
                return True, ""
            except Exception as exc:
                return False, str(exc)

        # System entry: create a per-user override; never edit /etc.
        try:
            cls._write_desktop(
                target, entry["name"], entry["exec"], hidden=not enabled
            )
            return True, ""
        except Exception as exc:
            return False, str(exc)

    @classmethod
    def add_startup(cls, name, command):
        safe = "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-") or "initra-app"
        target = Path.home() / ".config/autostart" / f"{safe}.desktop"
        cls._write_desktop(target, name, command, hidden=False)
        return target

    # ---------- drivers ----------
    @classmethod
    def pci_graphics(cls):
        if not shutil.which("lspci"):
            return ["lspci is not installed."]
        result = cls._run(["lspci", "-nnk"], 8)
        blocks = []
        current = []
        capture = False
        for line in result.stdout.splitlines():
            low = line.lower()
            if line and not line.startswith((" ", "\t")):
                if current and capture:
                    blocks.append("\n".join(current))
                current = [line]
                capture = any(x in low for x in ("vga compatible", "3d controller", "display controller"))
            elif current:
                current.append(line)
        if current and capture:
            blocks.append("\n".join(current))
        return blocks or ["No graphics controller detected."]

    @classmethod
    def ubuntu_driver_devices(cls):
        if not shutil.which("ubuntu-drivers"):
            return "ubuntu-drivers is not installed or not available."
        result = cls._run(["ubuntu-drivers", "devices"], 20)
        return (result.stdout + result.stderr).strip() or "No additional proprietary driver recommendation reported."

    @staticmethod
    def install_recommended_driver_command():
        return ["pkexec", "ubuntu-drivers", "install"]

    # ---------- extended system info ----------
    @classmethod
    def root_filesystem(cls):
        result = cls._run(["df", "-h", "/"], 5)
        lines = result.stdout.splitlines()
        return lines[-1] if len(lines) >= 2 else "Unavailable"

    @classmethod
    def graphics_summary(cls):
        blocks = cls.pci_graphics()
        first = blocks[0].splitlines()[0] if blocks else "Unavailable"
        return first.split(":", 2)[-1].strip() if ":" in first else first

    @classmethod
    def session_type(cls):
        return os.environ.get("XDG_SESSION_TYPE", "Unknown").capitalize()

    @classmethod
    def display_server(cls):
        return cls.session_type()

    @classmethod
    def hostname(cls):
        return os.uname().nodename

    @classmethod
    def shell(cls):
        return os.environ.get("SHELL", "Unknown")
