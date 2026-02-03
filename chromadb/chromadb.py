#!/usr/bin/env python3
"""
ChromaDB App - Standalone vector database server
Self-contained ChromaDB server with configurable folder access
"""
import chromadb
from chromadb.config import Settings
from pathlib import Path
import yaml
import sys

# Paths
HOME = Path.home()
APP_DIR = HOME / ".decyphertek.ai"
CONFIGS_DIR = APP_DIR / "configs"
APP_STORE_DIR = APP_DIR / "app-store"
CHROMADB_DIR = APP_STORE_DIR / "chromadb"
CONFIG_FILE = CONFIGS_DIR / "cdb-config.yaml"
DB_PATH = CHROMADB_DIR / "data"

def load_config():
    """Load ChromaDB configuration"""
    if not CONFIG_FILE.exists():
        # Create default config
        default_config = {
            "host": "localhost",
            "port": 8000,
            "persist_directory": str(DB_PATH),
            "allow_reset": False,
            "anonymized_telemetry": False,
            "allowed_folders": [
                str(HOME / "Documents"),
                str(HOME / "Downloads")
            ],
            "denied_folders": [
                str(HOME / ".ssh"),
                str(HOME / ".gnupg"),
                "/etc",
                "/root"
            ]
        }
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        return default_config
    
    return yaml.safe_load(CONFIG_FILE.read_text())

def check_folder_access(folder_path: str, config: dict) -> bool:
    """Check if folder access is allowed based on config"""
    folder = Path(folder_path).resolve()
    
    # Check denied folders first
    for denied in config.get("denied_folders", []):
        denied_path = Path(denied).resolve()
        if folder == denied_path or denied_path in folder.parents:
            return False
    
    # Check allowed folders
    allowed_folders = config.get("allowed_folders", [])
    if not allowed_folders:
        return True  # If no restrictions, allow all (except denied)
    
    for allowed in allowed_folders:
        allowed_path = Path(allowed).resolve()
        if folder == allowed_path or allowed_path in folder.parents:
            return True
    
    return False

def start_server():
    """Start ChromaDB HTTP server"""
    config = load_config()
    
    # Ensure data directory exists
    DB_PATH.mkdir(parents=True, exist_ok=True)
    
    print(f"[ChromaDB] Starting server...")
    print(f"[ChromaDB] Host: {config['host']}")
    print(f"[ChromaDB] Port: {config['port']}")
    print(f"[ChromaDB] Data: {config['persist_directory']}")
    print(f"[ChromaDB] Allowed folders: {len(config.get('allowed_folders', []))}")
    print(f"[ChromaDB] Denied folders: {len(config.get('denied_folders', []))}")
    
    # Create ChromaDB client with persistence
    settings = Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=config["persist_directory"],
        anonymized_telemetry=config.get("anonymized_telemetry", False),
        allow_reset=config.get("allow_reset", False)
    )
    
    client = chromadb.Client(settings)
    
    # Start HTTP server
    from chromadb.server.fastapi import FastAPI
    import uvicorn
    
    app = FastAPI(settings)
    
    print(f"[ChromaDB] Server ready at http://{config['host']}:{config['port']}")
    print(f"[ChromaDB] Press Ctrl+C to stop")
    
    uvicorn.run(
        app,
        host=config["host"],
        port=config["port"],
        log_level="info"
    )

if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n[ChromaDB] Server stopped")
        sys.exit(0)
    except Exception as e:
        print(f"[ChromaDB] Error: {e}")
        sys.exit(1)
