#!/usr/bin/env bash
set -euo pipefail
 
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
IMAGE_NAME="windows-builder"
DIST_DIR="$ROOT_DIR/dist"
LEGACY_DIST_DIR="$ROOT_DIR/.docker_dist_windows"
 
echo "=== Building Docker image ==="
docker build -t "$IMAGE_NAME" -f "$ROOT_DIR/release/windows/docker-windows.Dockerfile" "$ROOT_DIR"
 
echo "=== Running Windows build in Docker ==="
mkdir -p "$DIST_DIR"
rm -rf "$LEGACY_DIST_DIR"
 
docker run --rm \
    -v "$DIST_DIR:/app/dist" \
    "$IMAGE_NAME"

if [ ! -f "$DIST_DIR/app.exe" ] || [ ! -f "$DIST_DIR/app_debug.exe" ]; then
    echo "ERROR: Expected artifacts were not created in $DIST_DIR"
    ls -lah "$DIST_DIR"
    exit 1
fi
 
echo "=== Build complete! ==="
echo "Output directory: $DIST_DIR"
ls -lah "$DIST_DIR"