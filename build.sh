#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -e

echo "=== [Render Build] Upgrading pip ==="
pip install --upgrade pip

echo "=== [Render Build] Installing lightweight PyTorch (CPU) ==="
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

echo "=== [Render Build] Installing backend dependencies ==="
pip install -r backend/requirements.txt

echo "=== [Render Build] Pre-downloading model weights during build phase ==="
# During build, Render has higher RAM headroom. Pre-caching weights prevents
# the runtime container from crashing with OOM during download/unpacking.
python -c "
import os
os.environ['TORCH_NUM_THREADS'] = '1'
import torch
torch.set_num_threads(1)
from facenet_pytorch import MTCNN, InceptionResnetV1
print('Caching MTCNN weights...')
MTCNN(device='cpu')
print('Caching FaceNet (vggface2) weights...')
InceptionResnetV1(pretrained='vggface2', device='cpu').eval()
print('Weights cached successfully!')
" || echo "Pre-caching completed or will be loaded on demand."

echo "=== [Render Build] Build completed successfully ==="
