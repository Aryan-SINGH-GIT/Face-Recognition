#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -e

echo "=== [Render Build] Upgrading pip ==="
pip install --upgrade pip

echo "=== [Render Build] Installing lightweight PyTorch (CPU) ==="
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

echo "=== [Render Build] Installing backend dependencies ==="
pip install -r backend/requirements.txt

echo "=== [Render Build] Pre-downloading FaceNet weights to disk cache ==="
python -c "
import os, requests
torch_home = os.getenv('TORCH_HOME', os.path.expanduser('~/.cache/torch'))
checkpoints_dir = os.path.join(torch_home, 'checkpoints')
os.makedirs(checkpoints_dir, exist_ok=True)
dest = os.path.join(checkpoints_dir, '20180402-114759-vggface2.pt')
if not os.path.exists(dest) or os.path.getsize(dest) < 100000000:
    print('Downloading FaceNet weights (106MB) during build step...')
    url = 'https://github.com/timesler/facenet-pytorch/releases/download/v2.2.9/20180402-114759-vggface2.pt'
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(dest + '.tmp', 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*512):
                if chunk: f.write(chunk)
        os.replace(dest + '.tmp', dest)
    print('Weights successfully cached to disk!')
else:
    print('Weights already exist in cache.')
" || echo "Pre-caching skipped or will be downloaded on first inference."

echo "=== [Render Build] Build completed successfully ==="
