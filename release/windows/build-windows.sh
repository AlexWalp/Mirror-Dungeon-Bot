#!/usr/bin/env bash
set -euo pipefail
 
echo "=== Running PyInstaller in Wine ==="

WINE_CMD=""
for c in wine64 wine wine64-stable wine-stable /usr/lib/wine/wine64 /usr/lib/wine/wine; do
    if [ -x "$c" ]; then
        WINE_CMD="$c"
        break
    fi
done

if [ -z "$WINE_CMD" ]; then
    WINE_CMD="$(find /usr /opt -maxdepth 6 -type f \( -name wine -o -name wine64 -o -name wine-stable -o -name wine64-stable \) -perm -111 2>/dev/null | head -n 1)"
fi

if [ -z "$WINE_CMD" ]; then
    echo "ERROR: No Wine executable found in container."
    exit 1
fi

export PROJECT_ROOT=/app
 
# Clean previous builds
mkdir -p /app/dist
rm -f /app/dist/app.exe /app/dist/app_debug.exe
rm -rf /app/build
 
# Run PyInstaller
xvfb-run -a "$WINE_CMD" "C:\\Program Files\\Python311\\python.exe" -m PyInstaller \
    /app/release/windows/pyinstaller-windows.spec \
    --clean \
    --noconfirm \
    --distpath /app/dist \
    --workpath /app/build
 
# Wait for Wine to finish
wineserver -w
 
echo "=== Build complete ==="
ls -lah /app/dist/