import shutil
import subprocess

class ServiceManager:
    @staticmethod
    def available():
        return shutil.which("systemctl") is not None

    @staticmethod
    def state(unit):
        if not ServiceManager.available():
            return "Unavailable"
        try:
            r = subprocess.run(["systemctl", "is-active", unit], capture_output=True, text=True, timeout=3)
            return "Active" if r.stdout.strip() == "active" else "Inactive"
        except Exception:
            return "Unknown"

    @staticmethod
    def command(unit, enable):
        action = "enable" if enable else "disable"
        now = "--now"
        return ["pkexec", "systemctl", action, now, unit]
