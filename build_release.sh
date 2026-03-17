#!/usr/bin/env bash
set -e

APPNAME="CGrinder"
ARCH="x86_64"
APPDIR="$PWD/AppDir"
APPIMAGETOOL="$HOME/appimagetool-x86_64.AppImage"
DISTDIR="$PWD/dist"
DOCKER_OUTDIR="$PWD/.docker_dist"

mkdir -p "$APPDIR/usr/bin"
mkdir -p "$DISTDIR"
rm -rf "$DOCKER_OUTDIR"
mkdir -p "$DOCKER_OUTDIR"

if [ ! -x "$APPIMAGETOOL" ]; then
  echo "ERROR: appimagetool not found or not executable at: $APPIMAGETOOL"
  echo "Download it and run: chmod +x $APPIMAGETOOL"
  exit 1
fi

echo "=== Step 1: Building Docker image ==="
docker build -t cgrinder-builder .

echo "=== Step 2: Running PyInstaller inside Docker ==="
docker run --rm \
  -v "$DOCKER_OUTDIR":/output \
  -e INSIDE_DOCKER=1 \
  cgrinder-builder

echo "=== Step 3: Wrapping into AppImage on host ==="

if [ ! -d "$DOCKER_OUTDIR/app" ]; then
  echo "ERROR: Expected Docker build output directory not found: $DOCKER_OUTDIR/app"
  exit 1
fi

rm -rf "$APPDIR/usr/bin"/*
cp -a "$DOCKER_OUTDIR/app"/. "$APPDIR/usr/bin"/

rm -rf "$DOCKER_OUTDIR"

APPIMAGE_EXTRACT_AND_RUN=1 \
  "$APPIMAGETOOL" "$APPDIR" "$DISTDIR/CGrinder-x86_64.AppImage"

chmod +x "$DISTDIR/${APPNAME}-${ARCH}.AppImage"

echo "=== Done! Output: $DISTDIR/CGrinder-x86_64.AppImage ==="