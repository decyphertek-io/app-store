#!/bin/bash
set -e

echo "Building GLOBALTARIAN RPG..."

# Install UV if not present
if ! command -v uv &> /dev/null; then
    echo "Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create venv and install dependencies
echo "Creating virtual environment..."
uv venv --python 3.13

echo "Installing dependencies..."
uv pip install textual rich langchain langchain-openai langgraph pyinstaller

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist build *.spec

# Build with PyInstaller
echo "Building executable with PyInstaller..."
uv run pyinstaller \
    --onefile \
    --name globaltarian-rpg.app \
    --clean \
    --collect-all textual \
    --collect-all rich \
    --collect-all langchain \
    --collect-all langgraph \
    --hidden-import textual \
    --hidden-import rich \
    --hidden-import langchain \
    --hidden-import langgraph \
    globaltarian.py

# Cleanup
echo "Cleaning up build artifacts..."
rm -rf .venv build *.spec

echo ""
echo "✓ Build complete! Executable: dist/globaltarian-rpg.app"
echo "✓ Clean build - no .venv or artifacts left behind"
