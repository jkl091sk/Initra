# Initra Linux Setup Manager

**Your Linux. Ready your way.**

Initra is a modern desktop setup and maintenance manager for Linux. It brings system setup, software management, maintenance, profiles and diagnostics into one consistent interface.

## Initra 3.0 Stable

### Main sections

- **Dashboard** — overview, Health Check and system information
- **Setup** — setup plan, profiles, Backup & Restore and dotfiles
- **Software** — applications, updates, repositories and drivers
- **System** — GNOME tweaks, startup applications and services
- **Maintenance** — cleanup, diagnostics and history
- **Tools** — profile import/export, Command Preview and Linux compatibility
- **Settings** — application preferences and About

### Linux compatibility

Initra detects the current distribution, architecture, kernel, desktop environment and package manager.

Package-management compatibility is implemented for:

- Ubuntu / Debian / Linux Mint / Pop!_OS — **APT**
- Fedora and related RPM systems — **DNF**
- Arch Linux / Manjaro / EndeavourOS — **pacman**
- openSUSE family — **zypper**

Some distribution-specific features are capability-dependent. Ubuntu/Debian-family support is currently the most mature path.

### Safety

- Command Preview lets you inspect generated setup commands before applying them.
- Cleanup is selective and preview-first.
- Backup & Restore can create configuration restore points.
- GNOME tweaks are only applied when the required schemas/keys exist.
- Initra does not blindly replace distribution system files.

## Run from source

Requirements: Python 3, `python3-venv`, Linux desktop session.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Install in the application menu

```bash
chmod +x install_desktop.sh
./install_desktop.sh
```

## Version

**3.0.0 Stable**

## License

MIT License. See `LICENSE`.
