# Initra 3.1.0 — UI & Reliability Update

Initra 3.1 polishes the interface and strengthens the existing Linux setup and maintenance workflows.

### Highlights
- New dark pink Initra visual identity
- Independent rounded section tabs with the old full-width pane line removed
- Smooth page and tab transitions with an Animations preference
- Distro-aware setup, dry run and script export
- APT / DNF / pacman / zypper package workflows
- Improved native software, updates and repository handling
- Safer package-cache cleanup
- Hardened systemd service controls and driver detection
- Safer Startup Apps `.desktop` creation
- History retention pruning
- Backup & Restore, diagnostics, profiles and Command Preview retained

### Install

Extract the final v3.1 archive and run:

```bash
chmod +x install_desktop.sh
./install_desktop.sh
```

Or run directly from a Python virtual environment as described in the README.

### Final release check

Before publishing the `v3.1.0` tag, run the application locally on Linux and smoke-test all seven top-level sections and their tabs.
