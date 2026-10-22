from __future__ import annotations
import shlex


class CommandPreviewService:
    @staticmethod
    def format_command(command):
        return " ".join(shlex.quote(str(x)) for x in command)

    @classmethod
    def package_install(cls, packages, manager="apt"):
        packages = sorted(set(packages))
        if not packages:
            return ["# No packages selected"]
        quoted = " ".join(shlex.quote(x) for x in packages)
        if manager == "dnf":
            return ["sudo dnf makecache", f"sudo dnf install -y {quoted}"]
        if manager == "pacman":
            return [f"sudo pacman -S --needed --noconfirm {quoted}"]
        if manager == "zypper":
            return ["sudo zypper --non-interactive refresh",
                    f"sudo zypper --non-interactive install {quoted}"]
        return ["sudo apt-get update", f"sudo apt-get install -y {quoted}"]

    @classmethod
    def profile_preview(cls, profile, manager="apt"):
        rows = ["# Initra command preview", "# Nothing below is executed from this preview.", ""]
        packages = profile.get("packages", [])
        if packages:
            rows += cls.package_install(packages, manager) + [""]
        for service in profile.get("services", []):
            rows.append(f"sudo systemctl enable --now {shlex.quote(service)}")
        tweaks = profile.get("tweaks", {})
        mapping = {
            "animations": ("org.gnome.desktop.interface", "enable-animations"),
            "hot_corners": ("org.gnome.desktop.interface", "enable-hot-corners"),
        }
        if tweaks:
            rows.append("")
        for name, enabled in tweaks.items():
            if name in mapping:
                schema, key = mapping[name]
                rows.append(
                    f"gsettings set {shlex.quote(schema)} {shlex.quote(key)} "
                    f"{'true' if bool(enabled) else 'false'}"
                )
        if profile.get("dotfiles"):
            rows += ["", "# Dotfiles step is selected; file operations are reviewed separately."]
        return "\n".join(rows).strip()
