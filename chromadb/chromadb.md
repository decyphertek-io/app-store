# ChromaDB App

Standalone vector database server for RAG functionality. Self-contained ChromaDB with configurable folder access.

## Purpose

- **Vector Database**: Store and query document embeddings
- **RAG Support**: Provide context retrieval for AI agents
- **Local Storage**: All data stored in `~/.decyphertek.ai/app-store/chromadb/data`
- **Folder Security**: Configurable allowed/denied folder access

## Configuration

Edit `~/.decyphertek.ai/app-store/chromadb/config.json`:

```json
{
  "host": "localhost",
  "port": 8000,
  "persist_directory": "~/.decyphertek.ai/app-store/chromadb/data",
  "allow_reset": false,
  "anonymized_telemetry": false,
  "allowed_folders": [
    "~/Documents",
    "~/Downloads"
  ],
  "denied_folders": [
    "~/.ssh",
    "~/.gnupg",
    "/etc",
    "/root"
  ]
}
```

### Folder Access Control

- **allowed_folders**: Whitelist of folders that can be indexed/read
- **denied_folders**: Blacklist of folders that are always blocked
- Denied folders take precedence over allowed folders
- Default: Allow Documents and Downloads, deny sensitive system folders

## Usage

### Start Server

```bash
~/.decyphertek.ai/app-store/chromadb/chromadb.app
```

Server runs on `http://localhost:8000`

### Stop Server

Press `Ctrl+C`

## Integration

The RAG Chat MCP skill connects to this ChromaDB app automatically:

```
RAG Chat Skill → ChromaDB App → Vector Database
```

## Data Storage

- **Database**: `~/.decyphertek.ai/app-store/chromadb/data/`
- **Collections**: Organized by name
- **Persistence**: Data persists across restarts

## Security

- Runs locally on localhost only
- Folder access control prevents indexing sensitive directories
- No external network access required
- All data stays on your machine

## Requirements

- Python 3.12+ (bundled in executable)
- No system-wide installation needed
- Self-contained with all dependencies

## Documentation

https://docs.trychroma.com/
