#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

APPNAME="CGrinder"
ARCH="x86_64"
APPDIR="$ROOT_DIR/AppDir"
APPIMAGETOOL="$HOME/appimagetool-x86_64.AppImage"
DISTDIR="$ROOT_DIR/dist"

mkdir -p "$APPDIR/usr/bin"
mkdir -p "$DISTDIR"

if [ "$INSIDE_DOCKER" = "1" ]; then
    echo "Building executable inside Docker..."
  export PROJECT_ROOT="$ROOT_DIR"
    pyinstaller "$ROOT_DIR/release/linux/pyinstaller-linux.spec" \
      --clean \
      --distpath "/output" \
      --workpath "$ROOT_DIR/build" \
      --noconfirm
else
    echo "Building AppImage..."
    APPIMAGE_EXTRACT_AND_RUN=1 \
      "$APPIMAGETOOL" "$APPDIR" "$DISTDIR/CGrinder-x86_64.AppImage"

    echo "Making AppImage executable..."
    chmod +x "$DISTDIR/${APPNAME}-${ARCH}.AppImage"

    echo "Done!"
fi