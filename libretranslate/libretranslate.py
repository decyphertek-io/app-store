#!/usr/bin/env python3
"""
LibreTranslate App - Standalone translation server
Self-contained LibreTranslate server for offline translations
"""
from pathlib import Path
import sys
import subprocess

# Paths
HOME = Path.home()
APP_DIR = HOME / ".decyphertek.ai"
APP_STORE_DIR = APP_DIR / "app-store"
LT_DIR = APP_STORE_DIR / "libretranslate"
DATA_DIR = LT_DIR / "data"

def start_server():
    """Start LibreTranslate server"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    host = "localhost"
    port = 5000

    print(f"[LibreTranslate] Starting server...")
    print(f"[LibreTranslate] Host: {host}")
    print(f"[LibreTranslate] Port: {port}")
    print(f"[LibreTranslate] Data: {DATA_DIR}")
    print(f"[LibreTranslate] API: http://{host}:{port}/translate")
    print(f"[LibreTranslate] Press Ctrl+C to stop")

    from libretranslate.main import main as lt_main
    sys.argv = [
        "libretranslate",
        "--host", host,
        "--port", str(port),
        "--load-only", "en,es",
        "--data-dir", str(DATA_DIR),
    ]
    lt_main()

if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n[LibreTranslate] Server stopped")
        sys.exit(0)
    except Exception as e:
        print(f"[LibreTranslate] Error: {e}")
        sys.exit(1)
