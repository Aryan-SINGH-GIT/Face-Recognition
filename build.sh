#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -e

echo "=== [Render Build] Upgrading pip ==="
pip install --upgrade pip

echo "=== [Render Build] Installing lightweight PyTorch (CPU) to prevent disk & memory overflow ==="
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

echo "=== [Render Build] Installing backend dependencies ==="
pip install -r backend/requirements.txt

echo "=== [Render Build] Build completed successfully ==="
