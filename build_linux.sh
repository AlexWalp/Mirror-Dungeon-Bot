#!/usr/bin/env bash
set -e

APPNAME="CGrinder"
ARCH="x86_64"
APPDIR="$PWD/AppDir"
APPIMAGETOOL="$HOME/appimagetool-x86_64.AppImage"
DISTDIR="$PWD/dist"

mkdir -p "$APPDIR/usr/bin"
mkdir -p "$DISTDIR"

if [ "$INSIDE_DOCKER" = "1" ]; then
    echo "Building executable inside Docker..."
    pyinstaller build_linux.spec \
      --clean \
      --distpath "/output" \
      --workpath build \
      --noconfirm
else
    echo "Building AppImage..."
    APPIMAGE_EXTRACT_AND_RUN=1 \
      "$APPIMAGETOOL" "$APPDIR" "$DISTDIR/CGrinder-x86_64.AppImage"

    echo "Making AppImage executable..."
    chmod +x "$DISTDIR/${APPNAME}-${ARCH}.AppImage"

    echo "Done!"
fi