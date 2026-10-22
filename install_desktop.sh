#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$HOME/.local/share/initra"
BIN_DIR="$HOME/.local/bin"
APP_DESKTOP="$HOME/.local/share/applications/initra.desktop"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"

mkdir -p "$APP_DIR" "$BIN_DIR" "$(dirname "$APP_DESKTOP")" "$ICON_DIR"
cp -a "$ROOT/." "$APP_DIR/"
cp "$ROOT/assets/initra_256.png" "$ICON_DIR/initra.png"

cat > "$BIN_DIR/initra" <<EOF
#!/usr/bin/env bash
set -e
cd "$APP_DIR"
if [ ! -x ".venv/bin/python" ]; then
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
fi
exec .venv/bin/python main.py
EOF
chmod +x "$BIN_DIR/initra"

cat > "$APP_DESKTOP" <<EOF
[Desktop Entry]
Type=Application
Name=Initra
Comment=Linux Setup Manager
Exec=$BIN_DIR/initra
Icon=$ICON_DIR/initra.png
Terminal=false
Categories=System;Settings;Utility;
StartupNotify=true
EOF

chmod +x "$APP_DESKTOP"
command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$HOME/.local/share/applications" || true
echo "Initra installed. Open it from your application menu."
