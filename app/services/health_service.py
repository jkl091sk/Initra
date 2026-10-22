from __future__ import annotations
import shutil
import socket
import subprocess
from pathlib import Path
from app.services.distro_service import DistroService


class HealthService:
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

    @classmethod
    def failed_services(cls):
        if not shutil.which("systemctl"):
            return []
        result = cls._run([
            "systemctl", "--failed", "--no-legend", "--plain",
            "--type=service"
        ], 10)
        rows = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if line:
                rows.append(line)
        return rows

    @classmethod
    def broken_packages(cls):
        manager = DistroService().info["package_manager"]
        if manager == "apt" and shutil.which("dpkg"):
            result = cls._run(["dpkg", "--audit"], 10)
            return [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if manager == "pacman" and shutil.which("pacman"):
            result = cls._run(["pacman", "-Dk"], 15)
            if result.returncode != 0:
                return [line.strip() for line in result.stderr.splitlines() if line.strip()]
        return []

    @classmethod
    def pending_updates(cls):
        manager = DistroService().info["package_manager"]
        if manager == "apt":
            result = cls._run(["apt", "list", "--upgradable"], 20)
            return [
                line.split("/", 1)[0].strip()
                for line in result.stdout.splitlines()
                if line.strip() and not line.startswith("Listing")
            ]
        if manager == "dnf":
            result = cls._run(["dnf", "-q", "check-update"], 25)
            return [
                line.split()[0] for line in result.stdout.splitlines()
                if len(line.split()) >= 3 and not line.startswith("Last metadata")
            ]
        if manager == "pacman" and shutil.which("checkupdates"):
            result = cls._run(["checkupdates"], 25)
            return [line.split()[0] for line in result.stdout.splitlines() if line.strip()]
        if manager == "zypper":
            result = cls._run(["zypper", "--non-interactive", "list-updates"], 25)
            return [line for line in result.stdout.splitlines() if "|" in line and not line.lstrip().startswith("-")]
        return []

    @staticmethod
    def disk_status():
        usage = shutil.disk_usage("/")
        free_pct = (usage.free / usage.total * 100) if usage.total else 0
        return usage.free, usage.total, free_pct

    @staticmethod
    def network_status():
        # DNS + short TCP connection; no data is transmitted beyond connection setup.
        try:
            socket.getaddrinfo("kernel.org", 443)
        except OSError as exc:
            return False, f"DNS lookup failed: {exc}"
        try:
            with socket.create_connection(("kernel.org", 443), timeout=3):
                return True, "Network and DNS are reachable."
        except OSError as exc:
            return False, f"Connection failed: {exc}"

    @classmethod
    def apt_source_health(cls):
        sources = [Path("/etc/apt/sources.list")]
        d = Path("/etc/apt/sources.list.d")
        if d.exists():
            sources += list(d.glob("*.list")) + list(d.glob("*.sources"))
        readable = 0
        enabled = 0
        for path in sources:
            if not path.exists():
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
                readable += 1
                for line in text.splitlines():
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#"):
                        enabled += 1
            except OSError:
                pass
        return readable, enabled

    @staticmethod
    def human_size(value):
        size = float(value)
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if size < 1024 or unit == "TB":
                return f"{size:.1f} {unit}" if unit != "B" else f"{size:.0f} B"
            size /= 1024

    @classmethod
    def full_scan(cls):
        failed = cls.failed_services()
        broken = cls.broken_packages()
        updates = cls.pending_updates()
        free, total, free_pct = cls.disk_status()
        net_ok, net_message = cls.network_status()
        source_files, source_entries = cls.apt_source_health()

        checks = []

        checks.append({
            "name": "Package integrity",
            "ok": not broken,
            "severity": "critical" if broken else "ok",
            "detail": "No broken package state reported." if not broken
                      else f"{len(broken)} package issue line(s) reported by dpkg.",
            "data": broken,
        })
        checks.append({
            "name": "System services",
            "ok": not failed,
            "severity": "warning" if failed else "ok",
            "detail": "No failed system services." if not failed
                      else f"{len(failed)} failed service(s) detected.",
            "data": failed,
        })
        disk_ok = free_pct >= 10
        checks.append({
            "name": "Disk space",
            "ok": disk_ok,
            "severity": "warning" if not disk_ok else "ok",
            "detail": f"{cls.human_size(free)} free ({free_pct:.1f}% of root filesystem).",
            "data": [],
        })
        checks.append({
            "name": "Network",
            "ok": net_ok,
            "severity": "warning" if not net_ok else "ok",
            "detail": net_message,
            "data": [],
        })
        repo_ok = source_files > 0 and source_entries > 0
        checks.append({
            "name": "APT repositories",
            "ok": repo_ok,
            "severity": "warning" if not repo_ok else "ok",
            "detail": f"{source_files} source file(s), {source_entries} enabled entry/entries."
                      if repo_ok else "No enabled readable APT source entries were found.",
            "data": [],
        })
        updates_ok = len(updates) == 0
        checks.append({
            "name": "Updates",
            "ok": updates_ok,
            "severity": "info" if not updates_ok else "ok",
            "detail": "System is up to date." if updates_ok
                      else f"{len(updates)} package update(s) available.",
            "data": updates[:30],
        })

        score = 100
        if broken:
            score -= min(40, 15 + len(broken) * 5)
        if failed:
            score -= min(20, len(failed) * 5)
        if not disk_ok:
            score -= 15
        if not net_ok:
            score -= 10
        if not repo_ok:
            score -= 10
        if updates:
            score -= min(15, len(updates))
        score = max(0, score)

        if score >= 90:
            status = "Excellent"
        elif score >= 75:
            status = "Good"
        elif score >= 55:
            status = "Needs attention"
        else:
            status = "Action recommended"

        return {
            "score": score,
            "status": status,
            "checks": checks,
            "failed_services": failed,
            "broken_packages": broken,
            "updates": updates,
        }
