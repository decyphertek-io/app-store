# app-store

Source for Decyphertek-packaged apps: each top-level folder is one product, built in CI and shipped as standalone binaries on [Releases](https://github.com/decyphertek-io/app-store/releases).

## Layout

| Path | Role |
|------|------|
| `app.yaml` | Catalog: install paths, download URLs, enabled flags for the Decyphertek installer |
| `<app>/` | Entry script(s), bundled config, and anything that belongs in that build |
| `.github/workflows/` | Per-app workflows: uv, PyInstaller onefile, upload to a versioned release |

Artifacts are named `*.apps` (not `.app`) so GitHub accepts the uploads.

## Apps in this repo

- **chromadb** — ChromaDB wrapper (enabled in catalog by default)
- **argostranslate** — Argos Translate bundle
- **cloudtek** — Multi-cloud VM CLI (Libcloud / Bitwarden)

Bump versions in `app.yaml` when you cut releases so `release_url` and tags stay aligned.
