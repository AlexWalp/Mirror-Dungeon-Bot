FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV WINEARCH=win64
ENV WINEPREFIX=/wine
ENV WINEDEBUG=-all

# Install Wine and dependencies
RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        wget \
        xvfb \
        wine \
        wine64 \
        wine64-tools \
        wine32 \
        winbind && \
    rm -rf /var/lib/apt/lists/*

# Initialize Wine prefix
RUN mkdir -p /wine && \
    WINE_BIN="$( \
        for c in wine wine64 wine-stable wine64-stable /usr/lib/wine/wine64 /usr/lib/wine/wine; do \
            if [ -x "$c" ]; then echo "$c"; break; fi; \
        done \
    )" && \
    if [ -z "$WINE_BIN" ]; then \
        WINE_BIN="$(find /usr /opt -maxdepth 6 -type f \( -name wine -o -name wine64 -o -name wine-stable -o -name wine64-stable \) -perm -111 2>/dev/null | head -n 1)"; \
    fi && \
    if [ -z "$WINE_BIN" ]; then echo "ERROR: Wine executable not found on PATH"; exit 1; fi && \
    xvfb-run -a "$WINE_BIN" cmd /c echo Wine prefix initialized && \
    wineserver -w

# Install Python 3.11 in Wine
ARG PYTHON_VERSION=3.11.9
RUN wget -q "https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-amd64.exe" -O /tmp/python.exe && \
    WINE_BIN="$( \
        for c in wine wine64 wine-stable wine64-stable /usr/lib/wine/wine64 /usr/lib/wine/wine; do \
            if [ -x "$c" ]; then echo "$c"; break; fi; \
        done \
    )" && \
    if [ -z "$WINE_BIN" ]; then \
        WINE_BIN="$(find /usr /opt -maxdepth 6 -type f \( -name wine -o -name wine64 -o -name wine-stable -o -name wine64-stable \) -perm -111 2>/dev/null | head -n 1)"; \
    fi && \
    if [ -z "$WINE_BIN" ]; then echo "ERROR: Wine executable not found on PATH"; exit 1; fi && \
    xvfb-run -a "$WINE_BIN" /tmp/python.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 && \
    wineserver -w && \
    rm /tmp/python.exe

# Verify Python installation
RUN WINE_BIN="$( \
        for c in wine wine64 wine-stable wine64-stable /usr/lib/wine/wine64 /usr/lib/wine/wine; do \
            if [ -x "$c" ]; then echo "$c"; break; fi; \
        done \
    )" && \
    if [ -z "$WINE_BIN" ]; then \
        WINE_BIN="$(find /usr /opt -maxdepth 6 -type f \( -name wine -o -name wine64 -o -name wine-stable -o -name wine64-stable \) -perm -111 2>/dev/null | head -n 1)"; \
    fi && \
    if [ -z "$WINE_BIN" ]; then echo "ERROR: Wine executable not found on PATH"; exit 1; fi && \
    xvfb-run -a "$WINE_BIN" "C:\\Program Files\\Python311\\python.exe" --version

WORKDIR /app

# Copy and install Python dependencies
COPY release/windows/requirements-windows.txt /app/
RUN WINE_BIN="$( \
        for c in wine wine64 wine-stable wine64-stable /usr/lib/wine/wine64 /usr/lib/wine/wine; do \
            if [ -x "$c" ]; then echo "$c"; break; fi; \
        done \
    )" && \
    if [ -z "$WINE_BIN" ]; then \
        WINE_BIN="$(find /usr /opt -maxdepth 6 -type f \( -name wine -o -name wine64 -o -name wine-stable -o -name wine64-stable \) -perm -111 2>/dev/null | head -n 1)"; \
    fi && \
    if [ -z "$WINE_BIN" ]; then echo "ERROR: Wine executable not found on PATH"; exit 1; fi && \
    xvfb-run -a "$WINE_BIN" "C:\\Program Files\\Python311\\python.exe" -m pip install --upgrade pip && \
    xvfb-run -a "$WINE_BIN" "C:\\Program Files\\Python311\\python.exe" -m pip install pyinstaller && \
    xvfb-run -a "$WINE_BIN" "C:\\Program Files\\Python311\\python.exe" -m pip install -r /app/requirements-windows.txt && \
    wineserver -w

# Copy the entire project
COPY . /app/

# Build script will be run as CMD
CMD ["bash", "/app/release/windows/build-windows.sh"]