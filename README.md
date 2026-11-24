# Face Recognition System - Multimodal AI

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-ee4c2c)
![Faiss](https://img.shields.io/badge/Faiss-Vector%20DB-blueviolet)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

An Enterprise-grade Face Recognition and Verification System built using **MTCNN** (Multi-task Cascaded Convolutional Networks) for face detection, **FaceNet (InceptionResnetV1)** for deep facial feature extraction, and **Faiss** for ultra-fast vector similarity search. 

This repository contains the Machine Learning pipeline capable of zero-shot face enrollment and verification, achieving a highly accurate biometric authentication framework.

**Developer:** Aryan Singh (Reg No: 240410700030)  
**Semester:** 5th Semester  
**Project Track:** Face Recognition System Multimodal AI  

---

## 🌟 Key Features
- **Accurate Face Detection:** Uses MTCNN to locate, crop, and align faces from raw images, ignoring background noise.
- **Deep Feature Extraction:** Uses a FaceNet model pre-trained on `vggface2` to map faces into highly robust 512-dimensional embeddings.
- **Ultra-Fast Vector DB:** Utilizes Facebook AI Similarity Search (Faiss) to store embeddings and instantly match incoming faces against the database via L2 Euclidean Distance.
- **Evaluation & Model Benchmarking:** Includes Jupyter notebooks to generate ROC curves, calculate True Accept Rate (TAR) vs. False Accept Rate (FAR), and compare FaceNet against ArcFace, VGG-Face, MobileFaceNet, and LBPH.
- **Enterprise Design Docs:** Complete [High-Level Design (HLD)](docs/HIGH_LEVEL_DESIGN.md), [Low-Level Design (LLD)](docs/LOW_LEVEL_DESIGN.md), and [Entity-Relationship Diagram (ERD)](docs/ERD_DESIGN.md) with dark-mode Mermaid diagrams.

---

## 📂 Repository Structure

```text
face_recognition/
│
├── ml/                         # Core Machine Learning Pipeline
│   ├── dataset atelier 4/      # Local face dataset (Folders named by identity)
│   ├── notebooks/
│   │   ├── 01_Evaluation_TAR_FAR.ipynb               # Biometric Evaluation & ROC plotting
│   │   └── 02_Model_Comparison_and_Evaluation.ipynb  # Comparative Benchmarks (FaceNet, ArcFace, etc.)
│   ├── dataset.py              # PyTorch DataLoader for image ingestion
│   ├── face_encoder.py         # Extracts faces & builds the Faiss Vector Database
│   ├── faiss_manager.py        # Faiss indexing, saving, and searching logic
│   ├── test_match.py           # Verification script to test new faces against DB
│   └── requirements.txt        # Python dependencies
│
├── backend/                    # FastAPI Server (REST API, JWT Auth, SQLite Audit Logs)
├── frontend/                   # React Web App (Vite, Webcam HUD, Admin Dashboard)
├── docs/                       # System Architecture & Design Specifications
│   ├── VIVA_EXPLANATION_GUIDE.md # Comprehensive Viva, Math, Trade-offs & Theory Guide
│   ├── HIGH_LEVEL_DESIGN.md    # HLD: Architecture, AWS Deployment, Security & Workflows
│   ├── LOW_LEVEL_DESIGN.md     # LLD: Classes, Tensors, API Schemas & Sequence Diagrams
│   └── ERD_DESIGN.md           # ERD: Relational Schema & Faiss Hybrid Storage Model
└── README.md                   
```

---

## 🚀 Installation & Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/Aryan-SINGH-GIT/Face-Recognition.git
cd Face-Recognition
```

### 2. Backend Setup (FastAPI & ML Engine)
```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate   # On Linux/macOS: source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Start the FastAPI server (Runs on http://localhost:8000)
uvicorn app.main:app --reload --port 8000
```
Interactive API documentation is available at `http://localhost:8000/docs`.

### 3. Frontend Setup (React + Vite)
```bash
# In a separate terminal:
cd frontend
npm install
npm run dev   # Runs on http://localhost:5173
```

---

## ☁️ Deploy to Render

The repository includes a ready-to-use Render Blueprint (`render.yaml`) that configures both the FastAPI backend web service and the React frontend static site automatically.

### Option A: 1-Click Blueprint Deploy (Recommended)
1. Fork or push this repository to GitHub.
2. Go to [Render Dashboard](https://dashboard.render.com/) and click **New +** → **Blueprint**.
3. Connect your `Face-Recognition` repository.
4. Render will read `render.yaml` and provision:
   - **`face-recognition-backend`**: Python FastAPI Web Service (`uvicorn`, PyTorch CPU, Faiss, and SQLite/PostgreSQL).
   - **`face-recognition-frontend`**: React Vite Static Site with automatic SPA client-side routing.
5. Click **Apply** to deploy both services simultaneously.

### Option B: Deploy Backend & Frontend Separately on Render

#### Backend (Web Service):
- **Runtime:** `Python 3` (or `Docker`)
- **Build Command:** `bash build.sh`
- **Start Command:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables:**
  - `PYTHON_VERSION`: `3.11.9`
  - `JWT_SECRET`: *(Any secure random string)*
  - `ALLOWED_ORIGINS`: `https://your-frontend.onrender.com`

#### Frontend (Static Site):
- **Root Directory:** `frontend`
- **Build Command:** `npm install && npm run build`
- **Publish Directory:** `dist`
- **Redirects / Rewrites:** Rewrite `/*` to `/index.html` (for React Router)
- **Environment Variables:**
  - `VITE_API_URL`: `https://your-backend.onrender.com`

---

## 💻 Usage & Capabilities

1. **Face Access Terminal (`/`):** Stream live webcam frames to verify identity or self-enroll biometric profile with passive anti-spoofing protection.
2. **Admin Dashboard (`/dashboard`):** Real-time KPI metrics, verification pass rates, engine hardware configurations, and one-click Anti-Spoofing toggle.
3. **Identities Manager (`/identities`):** Admin portal to inspect, enroll, or delete registered identities and automatically trigger Faiss index reconstruction.
4. **Audit Logs (`/logs`):** Immutable compliance access logs recorded in SQLite relational database with status, timestamp, distance, and client IP.
5. **Biometric Benchmarking (`ml/notebooks/`):**
   - `01_Evaluation_TAR_FAR.ipynb`: Computes TAR at FAR=1%, FAR=10%, and plots ROC curve ($AUC = 98.6\%$).
   - `02_Model_Comparison_and_Evaluation.ipynb`: Comprehensive comparison between FaceNet, ArcFace, VGG-Face, MobileFaceNet, and LBPH with EER and decision frontiers.

---

## 🧠 Technical Architecture Decisions
* **Why MTCNN?** Multi-task Cascaded Convolutional Networks handle varying angles, poor lighting, and 5-point landmark eye alignment far better than traditional Haar Cascades.
* **Why FaceNet (Inception-ResNet-v1)?** Metric Triplet Loss projects faces onto a 512-dimensional $L_2$-normalized unit hypersphere, enabling instant zero-shot enrollment without model retraining.
* **Why Faiss (`IndexFlatL2`)?** Hardware-accelerated SIMD vector search in RAM delivers sub-millisecond nearest neighbor queries across thousands of face embeddings.
* **Why Passive Anti-Spoofing?** Laplacian variance and texture analysis reject printed photos, paper masks, and phone screen replays before neural inference runs.
