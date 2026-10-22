# Changelog

## 3.1.0 — UI & Reliability Update

- Removed the unwanted full-width QTabWidget pane line and unified tabs as independent rounded pills.
- Added subtle animated page and tab transitions that respect the Animations preference.
- Updated application metadata to report version 3.1.0.
- Improved keyboard focus and disabled-control styling.
- Removed legacy APT-only assumptions from setup, dry-run, script export and maintenance workflows.
- Added update detection for APT, DNF, pacman and zypper.
- Added distro-aware package installation, update, upgrade and cleanup command routing.
- Added distro-aware package-cache scanning and renamed the cleanup item to the neutral “Package cache”.
- Made History retention actually prune the local log according to the saved preference.
- Kept the new pink Initra visual identity consistent across the application and website.

## 3.0.0 — Stable

- Promoted the redesigned seven-section interface to Stable.
- Added Linux distribution and package-manager detection.
- Added compatibility for APT, DNF, pacman and zypper command generation.
- Added distro-aware setup command preview and shell export.
- Added selective storage cleanup safeguards.
- Added Backup & Restore and configuration recovery workflow.
- Added Health Check and diagnostics.
- Added Profiles 2.0 with import/export.
- Added Software, Updates, Repositories and Drivers tools.
- Added Tweaks, Startup Apps and Services management.
- Added desktop notifications when supported.
- Added Linux application-menu installer and uninstaller.
- Added First Run Wizard and Ctrl+K command palette.
- Consolidated the interface into Dashboard, Setup, Software, System,
  Maintenance, Tools and Settings.
