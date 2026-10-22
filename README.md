<div align="center">
  <img src="assets/initra-logo.svg" alt="Initra logo" width="300">

# Initra Linux Setup Manager

### Your Linux. Ready your way.

A modern Linux desktop application for setup, software management, maintenance, profiles and diagnostics — all in one place.

[![Release](https://img.shields.io/github/v/release/jkl091sk/Initra?label=release)](https://github.com/jkl091sk/Initra/releases/latest)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/UI-PySide6-41CD52?logo=qt&logoColor=white)](https://doc.qt.io/qtforpython-6/)
[![Linux](https://img.shields.io/badge/platform-Linux-FCC624?logo=linux&logoColor=black)](https://www.kernel.org/)
[![License](https://img.shields.io/github/license/jkl091sk/Initra)](LICENSE)

[Download latest release](https://github.com/jkl091sk/Initra/releases/latest) · [Official website](https://jkl091sk.github.io/Initra/) · [Changelog](CHANGELOG.md) · [Report an issue](https://github.com/jkl091sk/Initra/issues)
</div>

---

<div align="center">
  <img src="initra-showcase.jpg" alt="Initra Linux Setup Manager showcase" width="100%">
</div>

---

## About

**Initra** is a desktop control center designed to make Linux setup and everyday system maintenance easier. Instead of jumping between terminal commands and separate utilities, Initra brings common setup, software, system and maintenance tasks into a consistent graphical interface.

The current stable version is **Initra 3.1.0**.

## Features

| Area | What Initra provides |
| --- | --- |
| **Dashboard** | Overview, Health Check and system information |
| **Setup** | Setup Plan, reusable Profiles, Backup & Restore and dotfiles |
| **Software** | Applications, updates, repositories and driver tools |
| **System** | GNOME tweaks, startup applications and services |
| **Maintenance** | Selective cleanup, diagnostics and history |
| **Tools** | Import/export, Command Preview and Linux compatibility information |
| **Settings** | Application preferences and About information |

### More highlights

- First Run Wizard for a cleaner initial setup experience
- `Ctrl+K` command palette for quick navigation
- Smooth page and tab transitions with an Animations preference
- Command Preview before setup operations
- Import/export for reusable setup profiles
- Distro-aware package workflows for APT, DNF, pacman and zypper
- Desktop notifications when supported
- Linux application-menu installer
- Dark pink Initra interface powered by PySide6

## Linux compatibility

Initra detects the current Linux distribution, architecture, kernel, desktop environment and package manager.

| Distribution family | Package manager |
| --- | --- |
| Ubuntu / Debian / Linux Mint / Pop!_OS | **APT** |
| Fedora and related RPM systems | **DNF** |
| Arch Linux / Manjaro / EndeavourOS | **pacman** |
| openSUSE family | **zypper** |

> Some features are distribution- or desktop-specific and are enabled only when the required system capability exists. Ubuntu/Debian-family support is currently the most mature path.

## Safety

Initra is designed around previewing and limiting potentially destructive actions:

- **Command Preview** lets you inspect generated setup commands before applying them.
- **Cleanup** is selective and preview-first.
- **Backup & Restore** can create configuration restore points.
- **GNOME tweaks** are applied only when the required schemas and keys exist.
- Distribution-specific tools are not blindly executed on unrelated systems.
- Startup entries avoid silent overwrites and sanitize line-based Desktop Entry values.

## Installation

### Download the stable release

Download **Initra 3.1.0 Stable** from the [Releases page](https://github.com/jkl091sk/Initra/releases/latest), extract the archive, then run:

```bash
chmod +x install_desktop.sh
./install_desktop.sh
```

The installer adds Initra to your Linux application menu and prepares its user-local environment.

### Run from source

Requirements:

- Python 3
- `python3-venv`
- Linux desktop session

```bash
git clone https://github.com/jkl091sk/Initra.git
cd Initra
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Uninstall

```bash
chmod +x uninstall_desktop.sh
./uninstall_desktop.sh
```

## Project structure

```text
Initra/
├── app/
│   ├── models/
│   ├── services/
│   ├── styles/
│   ├── views/
│   └── workers/
├── assets/
├── packaging/
├── main.py
├── requirements.txt
├── install_desktop.sh
└── uninstall_desktop.sh
```

## Release

**Current stable release:** Initra 3.1.0 Stable

See [CHANGELOG.md](CHANGELOG.md) for release highlights. The v3.1 release package/tag can be published after the final local runtime check.

## License

Initra is available under the [MIT License](LICENSE).

---

<div align="center">
  <img src="assets/initra-icon.svg" alt="Initra" width="48"><br>
  <strong>Initra</strong><br>
  Your Linux. Ready your way.
</div>
