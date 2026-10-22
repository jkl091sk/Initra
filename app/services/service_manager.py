import shutil
import subprocess


class ServiceManager:
    @staticmethod
    def available():
        return shutil.which("systemctl") is not None

    @staticmethod
    def unit_exists(unit):
        if not ServiceManager.available():
            return False
        try:
            result = subprocess.run(
                ["systemctl", "show", unit, "--property=LoadState", "--value"],
                capture_output=True, text=True, timeout=4, check=False
            )
            return result.stdout.strip() not in {"", "not-found"}
        except Exception:
            return False

    @staticmethod
    def state(unit):
        if not ServiceManager.available():
            return "Unavailable"
        if not ServiceManager.unit_exists(unit):
            return "Not installed"
        try:
            result = subprocess.run(
                ["systemctl", "is-active", unit],
                capture_output=True, text=True, timeout=3, check=False
            )
            state = result.stdout.strip().lower()
            if state == "active":
                return "Active"
            if state in {"inactive", "failed", "activating", "deactivating", "reloading"}:
                return state.capitalize()
            return "Inactive"
        except Exception:
            return "Unknown"

    @staticmethod
    def command(unit, enable):
        if not ServiceManager.available() or not ServiceManager.unit_exists(unit):
            return None
        action = "enable" if enable else "disable"
        return ["pkexec", "systemctl", action, "--now", unit]
