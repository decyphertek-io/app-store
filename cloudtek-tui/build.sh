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
uv pip install pyyaml awscli google-cloud-compute google-cloud-storage azure-identity azure-mgmt-compute azure-mgmt-storage azure-mgmt-network azure-mgmt-resource c7n ansible-core pulumi pyinstaller

echo ""
echo "Cleaning previous build..."
rm -rf dist build *.spec

echo ""
echo "Building executable with PyInstaller..."
pyinstaller --onefile \
    --name cloudtek-tui.app \
    --clean \
    --collect-all awscli \
    --collect-all google.cloud \
    --collect-all azure.mgmt \
    --collect-all azure.identity \
    --collect-all c7n \
    --collect-all ansible \
    --collect-all pulumi \
    --copy-metadata awscli \
    --copy-metadata google-cloud-compute \
    --copy-metadata google-cloud-storage \
    --copy-metadata azure-identity \
    --copy-metadata azure-mgmt-compute \
    --copy-metadata azure-mgmt-storage \
    --copy-metadata azure-mgmt-network \
    --copy-metadata azure-mgmt-resource \
    --copy-metadata c7n \
    --copy-metadata ansible-core \
    --copy-metadata pulumi \
    cloudtek_tui.py

echo ""
echo "Cleaning up build artifacts..."
rm -rf .venv build *.spec

echo ""
echo "✓ Build complete! Executable: dist/cloudtek-tui.app"
echo "✓ Clean build - no .venv or artifacts left behind"
