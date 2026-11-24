import io
import sys
import gc
import torch
import numpy as np
from pathlib import Path
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
import faiss

# Ensure ml directory is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
ML_DIR = PROJECT_ROOT / "ml"
if str(ML_DIR) not in sys.path:
    sys.path.insert(0, str(ML_DIR))

from faiss_manager import FaissManager
from app.services.liveness_service import liveness_service

class FaceService:
    def __init__(
        self,
        index_path: Path = ML_DIR / "index.faiss",
        mapping_path: Path = ML_DIR / "identities.json",
        embedding_dim: int = 512,
        default_threshold: float = 1.2
    ):
        self.index_path = index_path
        self.mapping_path = mapping_path
        self.embedding_dim = embedding_dim
        self.default_threshold = default_threshold

        # Device selection (CPU or CUDA)
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        
        # Optimize CPU PyTorch threads to reduce memory footprint on 512MB RAM containers
        if self.device.type == "cpu":
            try:
                torch.set_num_threads(1)
                torch.set_num_interop_threads(1)
            except Exception:
                pass

        # Models
        self.mtcnn = None
        self.resnet = None
        self.faiss_manager = None
        self.is_loaded = False

    def init_faiss(self):
        """Loads lightweight Faiss vector index into memory (uses <2MB RAM)."""
        if self.faiss_manager is None:
            self.faiss_manager = FaissManager(
                index_path=str(self.index_path),
                mapping_path=str(self.mapping_path),
                embedding_dim=self.embedding_dim
            )

    def load_models(self):
        """Initializes and preheats MTCNN, InceptionResnetV1, and Faiss in memory with strict RAM limits."""
        if self.is_loaded:
            return

        print(f"[FaceService] Loading models on device: {self.device} (Memory optimized)")
        self.init_faiss()

        # Disable autograd globally to prevent gradient graph memory consumption
        torch.set_grad_enabled(False)
        
        # Initialize MTCNN detector
        self.mtcnn = MTCNN(
            image_size=160,
            margin=0,
            min_face_size=20,
            thresholds=[0.6, 0.7, 0.7],
            factor=0.709,
            post_process=True,
            device=self.device
        )

        # Initialize FaceNet encoder in evaluation mode
        self.resnet = InceptionResnetV1(pretrained="vggface2").eval().to(self.device)
        for param in self.resnet.parameters():
            param.requires_grad = False

        self.is_loaded = True
        gc.collect()
        print(f"[FaceService] Models loaded. Faiss vector count: {self.faiss_manager.index.ntotal}")

    def _extract_embedding(self, img: Image.Image) -> tuple[np.ndarray | None, str | None]:
        """Detects face and generates a 512-D FaceNet embedding using inference_mode for minimum RAM usage."""
        face_tensor = self.mtcnn(img)
        if face_tensor is None:
            return None, "No human face detected in the image"

        face_tensor = face_tensor.unsqueeze(0).to(self.device)
        with torch.inference_mode():
            embedding = self.resnet(face_tensor)

        embedding_np = embedding.squeeze().cpu().numpy().astype("float32")
        del face_tensor, embedding
        return embedding_np, None

    def verify_face(
        self,
        image_bytes: bytes,
        threshold: float | None = None,
        check_liveness: bool = True
    ) -> dict:
        """
        Verifies an uploaded face against the Faiss vector database with optional anti-spoofing check.
        """
        if not self.is_loaded:
            self.load_models()

        eff_threshold = threshold if threshold is not None else self.default_threshold

        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as e:
            return {
                "match_found": False,
                "identity": None,
                "distance": None,
                "confidence": None,
                "is_live": False,
                "liveness_score": 0.0,
                "status": "NO_FACE",
                "message": f"Invalid image format: {str(e)}"
            }

        # 1. Passive Anti-Spoofing / Liveness Analysis
        is_live = True
        liveness_score = 1.0
        if check_liveness:
            is_live, liveness_score, liveness_msg = liveness_service.evaluate_liveness(img)
            if not is_live:
                return {
                    "match_found": False,
                    "identity": None,
                    "distance": None,
                    "confidence": None,
                    "is_live": False,
                    "liveness_score": liveness_score,
                    "status": "SPOOF_DETECTED",
                    "message": liveness_msg
                }

        # 2. Extract Embedding
        embedding_np, err = self._extract_embedding(img)
        if err:
            return {
                "match_found": False,
                "identity": None,
                "distance": None,
                "confidence": None,
                "is_live": is_live,
                "liveness_score": liveness_score,
                "status": "NO_FACE",
                "message": err
            }

        # 3. Faiss Nearest-Neighbor Search
        results = self.faiss_manager.search(embedding_np, k=1, threshold=eff_threshold)
        
        if results:
            identity, dist = results[0]
            confidence = max(0.0, min(100.0, round((1.0 - (dist / (2.0 * eff_threshold))) * 100, 2)))
            return {
                "match_found": True,
                "identity": identity,
                "distance": round(dist, 4),
                "confidence": confidence,
                "is_live": is_live,
                "liveness_score": liveness_score,
                "status": "GRANTED",
                "message": f"Access Granted: Verified as '{identity}'"
            }
        else:
            return {
                "match_found": False,
                "identity": None,
                "distance": None,
                "confidence": None,
                "is_live": is_live,
                "liveness_score": liveness_score,
                "status": "DENIED",
                "message": f"Access Denied: Unrecognized person (Threshold: {eff_threshold})"
            }

    def enroll_face(self, image_bytes: bytes, identity_name: str) -> dict:
        """
        Enrolls a new identity embedding into the Faiss vector database.
        Includes Biometric De-duplication: Rejects if the same physical face is already enrolled.
        """
        if not self.is_loaded:
            self.load_models()

        clean_name = identity_name.strip().replace(" ", "_")
        if not clean_name:
            return {"success": False, "identity": "", "total_embeddings": 0, "message": "Identity name cannot be empty"}

        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as e:
            return {"success": False, "identity": clean_name, "total_embeddings": 0, "message": f"Invalid image format: {str(e)}"}

        embedding_np, err = self._extract_embedding(img)
        if err:
            return {"success": False, "identity": clean_name, "total_embeddings": 0, "message": err}

        # -------------------------------------------------------------
        # Biometric De-Duplication Check
        # -------------------------------------------------------------
        # Strict threshold 0.95 detects if this exact face already exists in the vector store
        if self.faiss_manager.index.ntotal > 0:
            existing_matches = self.faiss_manager.search(embedding_np, k=1, threshold=0.95)
            if existing_matches:
                matched_id, dist = existing_matches[0]
                if matched_id.lower() == clean_name.lower():
                    return {
                        "success": False,
                        "already_enrolled": True,
                        "identity": matched_id,
                        "distance": round(dist, 4),
                        "message": f"This face is already registered as '{matched_id}'. Please sign in instead."
                    }
                else:
                    return {
                        "success": False,
                        "already_enrolled": True,
                        "identity": matched_id,
                        "distance": round(dist, 4),
                        "message": f"Biometric duplicate: This face is already enrolled under identity '{matched_id}'. Duplicate registrations are prohibited."
                    }

        # Add to Faiss and persist to disk
        self.faiss_manager.add_embeddings([embedding_np], [clean_name])
        self.faiss_manager.save()

        total = self.faiss_manager.index.ntotal
        return {
            "success": True,
            "identity": clean_name,
            "total_embeddings": total,
            "message": f"Identity '{clean_name}' successfully enrolled into biometric database"
        }

    def delete_identity(self, identity_name: str) -> dict:
        """Removes an identity from the Faiss index and identities file."""
        if not self.is_loaded:
            self.load_models()

        clean_name = identity_name.strip()
        if clean_name not in self.faiss_manager.identities:
            return {
                "success": False,
                "identity": clean_name,
                "remaining_embeddings": self.faiss_manager.index.ntotal,
                "message": f"Identity '{clean_name}' not found in database"
            }

        total = self.faiss_manager.index.ntotal
        all_vectors = self.faiss_manager.index.reconstruct_n(0, total)
        
        keep_indices = [i for i, name in enumerate(self.faiss_manager.identities) if name != clean_name]
        
        new_index = faiss.IndexFlatL2(self.embedding_dim)
        if keep_indices:
            new_vectors = all_vectors[keep_indices]
            new_index.add(new_vectors)
            new_identities = [self.faiss_manager.identities[i] for i in keep_indices]
        else:
            new_identities = []

        self.faiss_manager.index = new_index
        self.faiss_manager.identities = new_identities
        self.faiss_manager.save()

        return {
            "success": True,
            "identity": clean_name,
            "remaining_embeddings": new_index.ntotal,
            "message": f"Successfully deleted identity '{clean_name}' and re-indexed vector database"
        }

    def get_identities(self) -> list[str]:
        """Returns sorted list of unique enrolled identities."""
        self.init_faiss()
        return sorted(list(set(self.faiss_manager.identities)))

    def get_stats(self) -> dict:
        """Returns operational statistics of the service without triggering heavy model load."""
        self.init_faiss()
        total_embeddings = self.faiss_manager.index.ntotal if self.faiss_manager else 0
        unique_identities = len(self.get_identities()) if self.faiss_manager else 0
        return {
            "models_loaded": self.is_loaded,
            "total_embeddings": total_embeddings,
            "total_unique_identities": unique_identities,
            "device": str(self.device),
            "threshold": self.default_threshold,
            "embedding_dim": self.embedding_dim,
            "model_name": "InceptionResnetV1 (vggface2)"
        }

face_service = FaceService()
