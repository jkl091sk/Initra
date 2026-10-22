# Initra 3.1.0 — UI & Reliability Update

Initra 3.1 focuses on polish, Linux compatibility and reliability across the existing application rather than adding unnecessary complexity.

## Highlights

- Removed the unwanted full-width tab pane line and changed section tabs to independent rounded pills.
- Added subtle page, startup and tab transition animations that respect **Settings → Animations**.
- Updated the application version and release metadata to 3.1.0.
- Made setup installation, dry run, script export, updates and cleanup distro-aware for APT, DNF, pacman and zypper.
- Improved native software and repository handling across supported package-manager families.
- Hardened service management and driver detection so unsupported capabilities fail safely.
- Hardened startup application creation to avoid silent `.desktop` overwrites and malformed line-based values.
- Made history retention prune old local entries according to the saved preference.
- Kept the new dark pink Initra identity consistent across the desktop application and website.

## Compatibility

Initra detects the active Linux distribution and package manager. Core package workflows support:

- Debian / Ubuntu / Linux Mint / Pop!_OS — APT
- Fedora and related systems — DNF
- Arch Linux / Manjaro / EndeavourOS — pacman
- openSUSE family — zypper

Some desktop- or distribution-specific tools remain conditional and are shown only when the required system capability is available.

## Before publishing the release

Run the final local smoke test on Linux, verify the main navigation and every section tab, then create the `v3.1.0` GitHub tag/release and attach the final release archive.
