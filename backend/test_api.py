import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Set up paths
BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

from app.main import app

# Entering context manager triggers the lifespan startup event
with TestClient(app) as client:
    print("\n--- 1. Testing GET /health ---")
    res = client.get("/health")
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.json()}")
    assert res.status_code == 200
    assert res.json()["models_loaded"] is True
    assert res.json()["total_embeddings"] > 0

    print("\n--- 2. Testing GET /identities ---")
    res = client.get("/identities")
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.json()}")
    assert res.status_code == 200
    assert len(res.json()["unique_identities"]) > 0

    print("\n--- 3. Testing GET /config ---")
    res = client.get("/config")
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.json()}")
    assert res.status_code == 200

    print("\n--- 4. Testing POST /verify with a real dataset image ---")
    test_image_path = Path("c:/D/face_recogonation/ml/dataset atelier 4/Bill_Frist/Bill_Frist_0001.jpg")
    if test_image_path.exists():
        with open(test_image_path, "rb") as f:
            res = client.post(
                "/verify",
                files={"file": ("Bill_Frist_0001.jpg", f, "image/jpeg")}
            )
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.json()}")
        assert res.status_code == 200
        assert res.json()["match_found"] is True
        assert res.json()["identity"] == "Bill_Frist"
        print("\n>>> ALL TESTS PASSED! Backend is 50% complete and fully verified! <<<\n")
    else:
        print(f"Warning: Test image not found at {test_image_path}")
