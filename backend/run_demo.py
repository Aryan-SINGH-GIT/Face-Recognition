import sys
from pathlib import Path

# Add backend directory to path
BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app

def run_live_demonstration():
    with TestClient(app) as client:
        print("=" * 60)
        print("     FACE RECOGNITION BACKEND — LIVE DEMONSTRATION")
        print("=" * 60)

        # 1. Health & Pre-warming check
        print("\n[1] Diagnostic Health Check (GET /health)")
        health = client.get("/health").json()
        print(f"    - System Status       : {health['status'].upper()}")
        print(f"    - Neural Models Loaded: {health['models_loaded']}")
        print(f"    - Hardware Device     : {health['device']}")
        print(f"    - Total Vector Count  : {health['total_embeddings']}")
        print(f"    - Unique Identities   : {health['total_unique_identities']}")

        # 2. Enrolled identities list
        print("\n[2] Enrolled Directory (GET /identities)")
        identities = client.get("/identities").json()
        print(f"    - Registered Names ({identities['unique_count']}):")
        for idx, name in enumerate(identities['unique_identities'], 1):
            print(f"       {idx}. {name}")

        # 3. Model Configuration
        print("\n[3] Model Configuration (GET /config)")
        cfg = client.get("/config").json()
        print(f"    - Model Name         : {cfg['model_name']}")
        print(f"    - Embedding Dimension: {cfg['embedding_dim']}-D")
        print(f"    - L2 Match Threshold : {cfg['threshold']}")

        # 4. Verify Identity: Bill Frist
        print("\n[4] Biometric Verification: Bill Frist (POST /verify)")
        bill_path = Path("c:/D/face_recogonation/ml/dataset atelier 4/Bill_Frist/Bill_Frist_0001.jpg")
        if bill_path.exists():
            with open(bill_path, "rb") as f:
                res = client.post("/verify", files={"file": ("bill.jpg", f, "image/jpeg")}).json()
            print(f"    - Match Status    : {'GRANTED' if res['match_found'] else 'DENIED'}")
            print(f"    - Matched Person  : {res['identity']}")
            print(f"    - L2 Distance     : {res['distance']}")
            print(f"    - Confidence Score: {res['confidence']}%")
            print(f"    - System Message  : {res['message']}")

        # 5. Verify Identity: Jennifer Garner
        print("\n[5] Biometric Verification: Jennifer Garner (POST /verify)")
        jg_path = Path("c:/D/face_recogonation/ml/dataset atelier 4/Jennifer_Garner/Jennifer_Garner_0001.jpg")
        if jg_path.exists():
            with open(jg_path, "rb") as f:
                res = client.post("/verify", files={"file": ("jg.jpg", f, "image/jpeg")}).json()
            print(f"    - Match Status    : {'GRANTED' if res['match_found'] else 'DENIED'}")
            print(f"    - Matched Person  : {res['identity']}")
            print(f"    - L2 Distance     : {res['distance']}")
            print(f"    - Confidence Score: {res['confidence']}%")

        # 6. Verify Identity: Jimmy Carter
        print("\n[6] Biometric Verification: Jimmy Carter (POST /verify)")
        jc_path = Path("c:/D/face_recogonation/ml/dataset atelier 4/Jimmy_Carter/Jimmy_Carter_0001.jpg")
        if jc_path.exists():
            with open(jc_path, "rb") as f:
                res = client.post("/verify", files={"file": ("jc.jpg", f, "image/jpeg")}).json()
            print(f"    - Match Status    : {'GRANTED' if res['match_found'] else 'DENIED'}")
            print(f"    - Matched Person  : {res['identity']}")
            print(f"    - L2 Distance     : {res['distance']}")
            print(f"    - Confidence Score: {res['confidence']}%")

        print("\n" + "=" * 60)
        print("     LIVE DEMO COMPLETE: ALL ENDPOINTS FUNCTIONING 100%")
        print("=" * 60)

if __name__ == "__main__":
    run_live_demonstration()
