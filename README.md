# Face Recognition System - Multimodal AI

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-ee4c2c)
![Faiss](https://img.shields.io/badge/Faiss-Vector%20DB-blueviolet)
![Status](https://img.shields.io/badge/Status-Phase%201%20Completed-success)

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
- **Evaluation & Metrics:** Includes Jupyter notebooks to generate ROC curves and calculate True Accept Rate (TAR) vs. False Accept Rate (FAR). Evaluated model achieved an **AUC of 98.6%**.

---

## 📂 Repository Structure

```text
face_recognition/
│
├── ml/                         # Core Machine Learning Pipeline
│   ├── dataset atelier 4/      # Local face dataset (Folders named by identity)
│   ├── notebooks/
│   │   └── 01_Evaluation_TAR_FAR.ipynb  # Biometric Evaluation & ROC plotting
│   ├── dataset.py              # PyTorch DataLoader for image ingestion
│   ├── face_encoder.py         # Extracts faces & builds the Faiss Vector Database
│   ├── faiss_manager.py        # Faiss indexing, saving, and searching logic
│   ├── test_match.py           # Verification script to test new faces against DB
│   └── requirements.txt        # Python dependencies
│
├── backend/                    # FastAPI Server (Upcoming Phase)
├── frontend/                   # React Web App (Upcoming Phase)
└── README.md                   
```

---

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/face-recognition-system.git
   cd face-recognition-system
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   
   # Windows Activation:
   .\venv\Scripts\Activate
   
   # Linux/Mac Activation:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   cd ml
   pip install -r requirements.txt
   ```
   *(Note: This installs PyTorch, Facenet-PyTorch, Faiss-CPU, Scikit-learn, and Matplotlib).*

---

## 💻 Usage Instructions

### 1. Build the Database (Face Enrollment)
Place images of people you want to recognize inside `ml/dataset atelier 4/` (one folder per person). Then, run the encoder to detect their faces and save their 512-D vectors into the Faiss index.
```bash
cd ml
python face_encoder.py
```
*Output: Generates `index.faiss` and `identities.json` in the `ml` folder.*

### 2. Test Face Verification
To check if a new image matches anyone in the database, pass the image path to the test script:
```bash
python test_match.py "path/to/test/image.jpg"
```
*Output: Crops the face, generates a new vector, searches Faiss, and returns the closest match identity and mathematical distance.*

### 3. Run the Evaluation Notebook
To view the mathematical accuracy of the model (ROC Curve and AUC score):
1. Open `ml/notebooks/01_Evaluation_TAR_FAR.ipynb` in VS Code or Jupyter.
2. Select your `venv` as the Python Kernel.
3. Run all cells to generate pairs, compute distances, and plot the True Accept Rate (TAR) vs. False Accept Rate (FAR) graphs.

---

## 🧠 Technical Architecture Decisions
* **Why MTCNN?** Better than traditional OpenCV Haar Cascades for handling poor lighting, varying angles, and facial alignment.
* **Why FaceNet over LBPH?** Deep Learning understands 3D facial geometry rather than just pixel intensity, making it highly robust to visual changes.
* **Why Faiss?** Allows scalable, millisecond-fast searches across millions of vectors, making this system enterprise-ready.

---

## 📈 Next Steps (Phase 3 & 4)
- **Phase 3:** Wrap the ML engine into a `FastAPI` REST server for asynchronous, HTTP-based verification.
- **Phase 4:** Build a `React` web interface to stream webcam video and visualize security dashboard results.
