# ==============================================================================
# Enterprise Face Recognition Backend - Dockerfile for Render / Cloud Containers
# ==============================================================================
FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV MALLOC_ARENA_MAX=2
ENV TORCH_NUM_THREADS=1
ENV OMP_NUM_THREADS=1

# Install essential Linux libraries for OpenCV (headless), Faiss, and C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install lightweight PyTorch CPU wheels
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install backend Python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Pre-cache model weights during container build
RUN python -c "from facenet_pytorch import MTCNN, InceptionResnetV1; MTCNN(device='cpu'); InceptionResnetV1(pretrained='vggface2', device='cpu').eval()" || true

# Copy backend and ML service modules into container
COPY backend /app/backend
COPY ml /app/ml

# Configure Python search path
ENV PYTHONPATH="/app/backend:/app/ml:${PYTHONPATH}"
ENV PORT=8000

WORKDIR /app/backend

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
