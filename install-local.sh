#!/usr/bin/env bash
set -e
APP_DIR="$HOME/.local/share/initra-app"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$APP_DIR" "$BIN_DIR" "$DESKTOP_DIR"
cp -r app assets main.py requirements.txt "$APP_DIR/"
python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"
cat > "$BIN_DIR/initra" <<EOF
#!/usr/bin/env bash
cd "$APP_DIR"
exec "$APP_DIR/.venv/bin/python" main.py
EOF
chmod +x "$BIN_DIR/initra"
cat > "$DESKTOP_DIR/initra.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Initra
Comment=Linux Setup Manager
Exec=$BIN_DIR/initra
Icon=$APP_DIR/assets/initra_256.png
Terminal=false
Categories=System;Settings;
EOF
echo "Initra installed. Launch it from your applications menu or run: $BIN_DIR/initra"

if [ -d "$HOME/Desktop" ]; then
    cp "$DESKTOP_DIR/initra.desktop" "$HOME/Desktop/Initra.desktop"
    chmod +x "$HOME/Desktop/Initra.desktop"
fi
