#!/bin/bash

set -e

echo "=== cloudtek-tui Build Script ==="
echo ""

if ! command -v uv &> /dev/null; then
    echo "⚠ uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "✓ uv: $(uv --version)"
echo ""

echo "Installing dependencies with uv (Python 3.13)..."
uv venv --clear --python 3.13
source .venv/bin/activate
uv pip install setuptools wheel
uv pip install textual pyyaml awscli azure-cli c7n ansible-core pulumi pyinstaller

echo ""
echo "Cleaning previous build..."
rm -rf dist build *.spec

echo ""
echo "Building executable with PyInstaller..."
pyinstaller --onefile \
    --name cloudtek-tui.app \
    --clean \
    --hidden-import awscli \
    --hidden-import azure.cli \
    --hidden-import c7n \
    --hidden-import ansible \
    --collect-all textual \
    --collect-all rich \
    --copy-metadata rich \
    cloudtek_tui.py

echo ""
echo "Cleaning up build artifacts..."
rm -rf .venv build *.spec

echo ""
echo "✓ Build complete! Executable: dist/cloudtek-tui.app"
echo "✓ Clean build - no .venv or artifacts left behind"
