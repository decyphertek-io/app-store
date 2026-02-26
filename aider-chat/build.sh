#!/bin/bash

set -eo pipefail

echo "=== aider-chat Build Script ==="
echo ""

if ! command -v uv &> /dev/null; then
    echo "uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "uv: $(uv --version)"
echo ""

echo "Installing dependencies with uv (Python 3.12)..."
uv venv --clear --python 3.12
source .venv/bin/activate
uv pip install aider-chat pyyaml pyinstaller cryptography python-multipart

echo ""
echo "Cleaning previous build..."
rm -rf dist build *.spec

echo ""
echo "Building executable with PyInstaller..."
pyinstaller --onefile \
    --name aider-chat.app \
    --clean \
    --collect-all aider \
    --collect-all litellm \
    --collect-all tiktoken \
    --collect-all rich \
    --add-data ".venv/lib/python3.12/site-packages/tiktoken_ext:tiktoken_ext" \
    --collect-submodules aider \
    --collect-submodules tiktoken \
    --collect-submodules litellm \
    --hidden-import aider.main \
    --hidden-import aider.coders \
    --hidden-import aider.models \
    --hidden-import aider.io \
    --hidden-import aider.repo \
    --hidden-import aider.versioncheck \
    --hidden-import litellm.litellm_core_utils.tokenizers \
    --hidden-import litellm.litellm_core_utils \
    --hidden-import tiktoken_ext \
    --hidden-import tiktoken_ext.openai_public \
    --copy-metadata aider-chat \
    --copy-metadata litellm \
    --copy-metadata tiktoken \
    launcher.py

echo ""
echo "Cleaning up build artifacts..."
rm -rf .venv build
find . -maxdepth 1 -name "*.spec" -delete

echo ""
echo "Build complete! Executable: dist/aider-chat.app"
echo "Clean build - no .venv or artifacts left behind"
echo ""
echo "Install to decyphertek.ai app-store:"
echo "  mkdir -p ~/.decyphertek.ai/app-store/aider-chat"
echo "  cp dist/aider-chat.app ~/.decyphertek.ai/app-store/aider-chat/"
echo "  ln -sf ~/.decyphertek.ai/app-store/aider-chat/aider-chat.app ~/.local/bin/aider-chat.app"
