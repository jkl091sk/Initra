import os
import platform
import shutil
import subprocess

class SystemInfoService:
    @staticmethod
    def _os_release():
        data = {}
        try:
            with open("/etc/os-release", encoding="utf-8") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.rstrip().split("=", 1)
                        data[k] = v.strip('"')
        except OSError:
            pass
        return data

    @classmethod
    def pretty_name(cls):
        return cls._os_release().get("PRETTY_NAME", "Linux")

    @staticmethod
    def architecture():
        return platform.machine()

    @staticmethod
    def package_manager():
        for cmd in ("apt", "dnf", "pacman", "zypper"):
            if shutil.which(cmd):
                return cmd
        return "unknown"

    @staticmethod
    def desktop():
        return os.environ.get("XDG_CURRENT_DESKTOP", "Unknown").replace(":", " / ")

    @staticmethod
    def kernel():
        return platform.release()

    @staticmethod
    def hostname():
        return platform.node() or "Linux PC"

    @staticmethod
    def memory():
        try:
            with open("/proc/meminfo", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        kb = int(line.split()[1])
                        return f"{kb / 1024 / 1024:.1f} GB RAM"
        except (OSError, ValueError):
            pass
        return "Unknown RAM"

    @staticmethod
    def cpu():
        try:
            with open("/proc/cpuinfo", encoding="utf-8") as f:
                for line in f:
                    if line.lower().startswith("model name"):
                        return line.split(":", 1)[1].strip()
        except OSError:
            pass
        return platform.processor() or "Unknown CPU"

    @staticmethod
    def disk_free():
        try:
            total, used, free = shutil.disk_usage("/")
            return f"{free / 1024**3:.0f} GB free"
        except OSError:
            return "Unknown"

    @staticmethod
    def service_state(name):
        if not shutil.which("systemctl"):
            return "Unavailable"
        try:
            r = subprocess.run(
                ["systemctl", "is-active", name],
                capture_output=True, text=True, timeout=2, check=False
            )
            return "Active" if r.stdout.strip() == "active" else "Inactive"
        except Exception:
            return "Unknown"
