#!/usr/bin/env bash
set -euo pipefail
rm -f "$HOME/.local/bin/initra"
rm -f "$HOME/.local/share/applications/initra.desktop"
rm -f "$HOME/.local/share/icons/hicolor/256x256/apps/initra.png"
rm -rf "$HOME/.local/share/initra"
echo "Initra application files removed. User settings/backups under ~/.config and ~/.local/share/initra may already be removed with the app directory."
