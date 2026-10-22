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
            return subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
        except Exception as exc:
            class Result:
                returncode = 1
                stdout = ""
                stderr = str(exc)
            return Result()

    @classmethod
    def gsettings_available(cls): return shutil.which("gsettings") is not None
    @classmethod
    def schema_exists(cls, schema):
        if not cls.gsettings_available(): return False
        return schema in cls._run(["gsettings", "list-schemas"], 5).stdout.splitlines()
    @classmethod
    def key_exists(cls, schema, key):
        if not cls.schema_exists(schema): return False
        return key in cls._run(["gsettings", "list-keys", schema], 5).stdout.splitlines()
    @classmethod
    def get_setting(cls, schema, key):
        if not cls.key_exists(schema, key): return None
        result = cls._run(["gsettings", "get", schema, key], 5)
        return result.stdout.strip() if result.returncode == 0 else None
    @classmethod
    def set_setting(cls, schema, key, value):
        if not cls.key_exists(schema, key): return False, f"{schema}:{key} is not available on this desktop."
        result = cls._run(["gsettings", "set", schema, key, value], 5)
        return result.returncode == 0, (result.stderr.strip() or result.stdout.strip())

    @staticmethod
    def startup_dirs(): return [(Path.home()/".config/autostart", True), (Path("/etc/xdg/autostart"), False)]
    @classmethod
    def startup_entries(cls):
        entries=[]; seen=set()
        for directory,user_owned in cls.startup_dirs():
            if not directory.exists(): continue
            for file in sorted(directory.glob("*.desktop")):
                if file.name in seen: continue
                seen.add(file.name); parser=configparser.ConfigParser(interpolation=None, strict=False)
                try: parser.read(file,encoding="utf-8"); sec=parser["Desktop Entry"]
                except Exception: continue
                entries.append({"file":file,"name":sec.get("Name",file.stem),"exec":sec.get("Exec",""),"hidden":sec.get("Hidden","false").lower()=="true","user_owned":user_owned})
        return entries

    @staticmethod
    def _desktop_value(value):
        # Desktop Entry values are line based. Reject embedded control lines so
        # user-entered names/commands cannot accidentally create extra keys.
        return str(value).replace("\r", " ").replace("\n", " ").strip()

    @classmethod
    def _write_desktop(cls,path,name,command,hidden=False):
        name=cls._desktop_value(name); command=cls._desktop_value(command)
        if not name or not command: raise ValueError("Application name and command must not be empty.")
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text("[Desktop Entry]\nType=Application\n"+f"Name={name}\nExec={command}\nHidden={'true' if hidden else 'false'}\nX-GNOME-Autostart-enabled=true\n",encoding="utf-8")

    @classmethod
    def set_startup_enabled(cls,entry,enabled):
        target=Path.home()/".config/autostart"/entry["file"].name
        if entry["user_owned"]:
            try:
                parser=configparser.ConfigParser(interpolation=None,strict=False); parser.optionxform=str; parser.read(entry["file"],encoding="utf-8")
                if "Desktop Entry" not in parser: parser["Desktop Entry"]={}
                parser["Desktop Entry"]["Hidden"]="false" if enabled else "true"
                with entry["file"].open("w",encoding="utf-8") as f: parser.write(f,space_around_delimiters=False)
                return True,""
            except Exception as exc: return False,str(exc)
        try: cls._write_desktop(target,entry["name"],entry["exec"],hidden=not enabled); return True,""
        except Exception as exc: return False,str(exc)

    @classmethod
    def add_startup(cls,name,command):
        name=cls._desktop_value(name); command=cls._desktop_value(command)
        if not name or not command: raise ValueError("Application name and command must not be empty.")
        safe="".join(c.lower() if c.isalnum() else "-" for c in name).strip("-") or "initra-app"
        directory=Path.home()/".config/autostart"; target=directory/f"{safe}.desktop"; suffix=2
        # Never silently overwrite an existing autostart entry with the same
        # display name. Preserve it and choose a deterministic free filename.
        while target.exists():
            target=directory/f"{safe}-{suffix}.desktop"; suffix+=1
        cls._write_desktop(target,name,command,False); return target

    @classmethod
    def pci_graphics(cls):
        if not shutil.which("lspci"): return ["lspci is not installed."]
        result=cls._run(["lspci","-nnk"],8); blocks=[]; current=[]; capture=False
        for line in result.stdout.splitlines():
            low=line.lower()
            if line and not line.startswith((" ","\t")):
                if current and capture: blocks.append("\n".join(current))
                current=[line]; capture=any(x in low for x in ("vga compatible","3d controller","display controller"))
            elif current: current.append(line)
        if current and capture: blocks.append("\n".join(current))
        return blocks or ["No graphics controller detected."]

    @classmethod
    def driver_report(cls, distro_id=""):
        blocks=cls.pci_graphics(); report=["GRAPHICS DEVICES","───────────────","\n\n".join(blocks)]
        distro=(distro_id or "").lower()
        if shutil.which("ubuntu-drivers"):
            result=cls._run(["ubuntu-drivers","devices"],20); text=(result.stdout+result.stderr).strip() or "No additional proprietary driver recommendation reported."
            report += ["","UBUNTU DRIVER RECOMMENDATIONS","─────────────────────────────",text]
        elif distro in {"ubuntu","pop","linuxmint","elementary","zorin"}:
            report += ["","DRIVER RECOMMENDATIONS","──────────────────────","ubuntu-drivers is not installed. Install the distro driver utility to query proprietary recommendations."]
        else:
            report += ["","DRIVER INFORMATION","──────────────────","Initra detected the graphics hardware above. Automatic proprietary-driver installation is intentionally unavailable on this distribution; use its native driver/package tooling."]
        return "\n".join(report)

    @classmethod
    def can_install_recommended_driver(cls): return shutil.which("ubuntu-drivers") is not None
    @classmethod
    def ubuntu_driver_devices(cls):
        if not cls.can_install_recommended_driver(): return "ubuntu-drivers is not installed or not available."
        result=cls._run(["ubuntu-drivers","devices"],20); return (result.stdout+result.stderr).strip() or "No additional proprietary driver recommendation reported."
    @classmethod
    def install_recommended_driver_command(cls):
        if not cls.can_install_recommended_driver(): return None
        return ["pkexec","ubuntu-drivers","install"]

    @classmethod
    def root_filesystem(cls):
        result=cls._run(["df","-h","/"],5); lines=result.stdout.splitlines(); return lines[-1] if len(lines)>=2 else "Unavailable"
    @classmethod
    def graphics_summary(cls):
        blocks=cls.pci_graphics(); first=blocks[0].splitlines()[0] if blocks else "Unavailable"; return first.split(":",2)[-1].strip() if ":" in first else first
    @classmethod
    def session_type(cls): return os.environ.get("XDG_SESSION_TYPE","Unknown").capitalize()
    @classmethod
    def display_server(cls): return cls.session_type()
    @classmethod
    def hostname(cls): return os.uname().nodename
    @classmethod
    def shell(cls): return os.environ.get("SHELL","Unknown")
