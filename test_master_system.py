import os
import sys
import time
import json
import urllib.request
import requests
from pathlib import Path

BASE_BACKEND = "http://127.0.0.1:8000"
BASE_FRONTEND = "http://localhost:5173"

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_master():
    print_header("MASTER SYSTEM TEST: BIOMETRIC ACCESS CONTROL PLATFORM")
    passed = 0
    total = 0

    dataset_dir = Path(r"c:\D\face_recogonation\ml\dataset atelier 4")

    # -------------------------------------------------------------
    # TEST 1: FRONTEND ACCESSIBILITY
    # -------------------------------------------------------------
    total += 1
    print("\n[TEST 1] Verifying React Frontend on http://localhost:5173 ...")
    try:
        r = requests.get(BASE_FRONTEND, timeout=5)
        if r.status_code == 200 and "<html" in r.text.lower():
            print("  [PASS] React Frontend is responding with HTTP 200 OK.")
            print(f"         Title/Doc length: {len(r.text)} bytes")
            passed += 1
        else:
            print(f"  [FAIL] Unexpected response: {r.status_code}")
    except Exception as e:
        print(f"  [FAIL] Frontend connection error: {e}")

    # -------------------------------------------------------------
    # TEST 2: BACKEND HEALTH & PRE-WARMED NEURAL MODELS
    # -------------------------------------------------------------
    total += 1
    print("\n[TEST 2] Verifying FastAPI Backend Health & Model Pre-warming ...")
    try:
        r = requests.get(f"{BASE_BACKEND}/health", timeout=5)
        d = r.json()
        assert r.status_code == 200
        assert d["status"] == "ok"
        assert d["models_loaded"] is True
        print(f"  [PASS] Backend Healthy! Status: {d['status']}, Device: {d['device']}")
        print(f"         Total Vectors in Faiss: {d['total_embeddings']}, Unique Identities: {d['total_unique_identities']}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Health check error: {e}")

    # -------------------------------------------------------------
    # TEST 3: SYSTEM CONFIG & HYPERPARAMETERS
    # -------------------------------------------------------------
    total += 1
    print("\n[TEST 3] Verifying Biometric Engine Configuration ...")
    try:
        r = requests.get(f"{BASE_BACKEND}/config", timeout=5)
        d = r.json()
        assert r.status_code == 200
        assert d["embedding_dim"] == 512
        assert d["threshold"] == 1.2
        assert d["liveness_enabled"] is True
        print(f"  [PASS] Model: {d['model_name']}, Dim: {d['embedding_dim']}, L2 Threshold: {d['threshold']}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Config check error: {e}")

    # -------------------------------------------------------------
    # TEST 4: ADMIN JWT AUTHENTICATION
    # -------------------------------------------------------------
    total += 1
    print("\n[TEST 4] Testing Admin Authentication & JWT Bearer Generation ...")
    token = None
    try:
        r = requests.post(f"{BASE_BACKEND}/auth/login", json={"username": "admin", "password": "admin123"}, timeout=5)
        d = r.json()
        assert r.status_code == 200
        assert "access_token" in d
        assert d["role"] == "SUPER_ADMIN"
        token = d["access_token"]
        print(f"  [PASS] Admin Login Successful! Role: {d['role']}")
        print(f"         JWT Token: {token[:25]}... (valid 8 hours)")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Admin login error: {e}")

    auth_headers = {"Authorization": f"Bearer {token}"} if token else {}

    # -------------------------------------------------------------
    # TEST 5: CORE MULTI-PERSON FACE VERIFICATION (/verify)
    # -------------------------------------------------------------
    test_identities = [
        ("Jimmy_Carter", dataset_dir / "Jimmy_Carter" / "Jimmy_Carter_0001.jpg"),
        ("Jennifer_Garner", dataset_dir / "Jennifer_Garner" / "Jennifer_Garner_0001.jpg"),
        ("Bill_Frist", dataset_dir / "Bill_Frist" / "Bill_Frist_0001.jpg"),
    ]

    for name, img_path in test_identities:
        total += 1
        print(f"\n[TEST 5.{name}] Testing Core Biometric Verification for {name} ...")
        try:
            with open(img_path, "rb") as f:
                r = requests.post(
                    f"{BASE_BACKEND}/verify",
                    files={"file": ("photo.jpg", f, "image/jpeg")},
                    params={"check_liveness": True},
                    timeout=15
                )
            d = r.json()
            assert r.status_code == 200
            assert d["match_found"] is True
            assert d["identity"] == name
            assert d["status"] == "GRANTED"
            assert d["is_live"] is True
            print(f"  [PASS] Verified: '{d['identity']}' | Status: {d['status']} | Confidence: {d['confidence']}% | L2 Dist: {d['distance']}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] Verification error for {name}: {e}")

    # -------------------------------------------------------------
    # TEST 6: USER PORTAL BIOMETRIC DUPLICATE ENROLLMENT CHECK (/user/register)
    # -------------------------------------------------------------
    total += 1
    print("\n[TEST 6] Testing Biometric Duplicate Prevention on Self-Registration ...")
    test_new_user = f"MasterTest_User_{int(time.time())}"
    enroll_img = dataset_dir / "Vaclav_Havel" / "Vaclav_Havel_0001.jpg"
    try:
        with open(enroll_img, "rb") as f:
            r = requests.post(
                f"{BASE_BACKEND}/user/register",
                data={"full_name": test_new_user, "display_name": "Master Tester"},
                files={"file": ("user_face.jpg", f, "image/jpeg")},
                timeout=15
            )
        # Biometric de-duplication must block registering an already-enrolled face under a new name
        assert r.status_code == 409, f"Expected 409 Conflict, got {r.status_code}"
        assert "Biometric duplicate" in r.json().get("detail", "")
        print(f"  [PASS] Biometric Duplicate Correctly Blocked with 409 Conflict!")
        print(f"         Detail: {r.json().get('detail')}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Biometric duplicate test error: {e}")

    # -------------------------------------------------------------
    # TEST 7: USER PORTAL FACE SIGN-IN (/user/login)
    # -------------------------------------------------------------
    total += 1
    print("\n[TEST 7] Testing User Portal Face Sign-In (/user/login) ...")
    try:
        with open(enroll_img, "rb") as f:
            r = requests.post(
                f"{BASE_BACKEND}/user/login",
                files={"file": ("login_face.jpg", f, "image/jpeg")},
                timeout=15
            )
        d = r.json()
        assert r.status_code == 200
        assert d["granted"] is True
        assert d["status"] == "GRANTED"
        print(f"  [PASS] Face Sign-In Successful! Recognized: '{d.get('identity') or d.get('full_name')}'")
        print(f"         Confidence: {d['confidence']}% | Message: {d['message']}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Face Sign-In error: {e}")

    # -------------------------------------------------------------
    # TEST 8: REGISTERED USER DIRECTORY (/user/list)
    # -------------------------------------------------------------
    total += 1
    print("\n[TEST 8] Testing GET /user/list ...")
    try:
        r = requests.get(f"{BASE_BACKEND}/user/list", timeout=5)
        d = r.json()
        assert r.status_code == 200
        assert d["total"] >= 1
        print(f"  [PASS] Directory retrieved! Found {d['total']} self-registered user(s).")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] User list error: {e}")

    # -------------------------------------------------------------
    # TEST 9: AUDIT LOG RETRIEVAL & FILTERING (/logs)
    # -------------------------------------------------------------
    total += 1
    print("\n[TEST 9] Testing Security Audit Logs with GRANTED filter ...")
    try:
        r = requests.get(f"{BASE_BACKEND}/logs?status_filter=GRANTED&limit=5", timeout=5)
        d = r.json()
        assert r.status_code == 200
        assert d["total"] > 0
        latest = d["logs"][0]
        print(f"  [PASS] Audit logs verified! Total GRANTED events: {d['total']}")
        print(f"         Latest log event: [{latest['timestamp'][:19]}] {latest['matched_identity']} ({latest['confidence_score']}%)")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Audit logs error: {e}")

    # -------------------------------------------------------------
    # TEST 10: REAL-TIME ANALYTICS SUMMARY (/analytics/summary)
    # -------------------------------------------------------------
    total += 1
    print("\n[TEST 10] Testing Real-Time Analytics & KPIs (/analytics/summary) ...")
    try:
        r = requests.get(f"{BASE_BACKEND}/analytics/summary", timeout=5)
        d = r.json()
        assert r.status_code == 200
        assert d["total_verifications"] > 0
        print(f"  [PASS] Total Scans: {d['total_verifications']} | Granted: {d['granted_count']} | Denied: {d['denied_count']}")
        print(f"         Pass Rate: {d['pass_rate_percentage']}% | Active Enrolled: {d['enrolled_identities_count']}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Analytics error: {e}")

    # -------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------
    print_header(f"TEST RESULTS: {passed}/{total} TESTS PASSED ({round(passed/total*100, 1)}%)")
    if passed == total:
        print("  ALL ENDPOINTS, ML PIPELINES, USER INTERFACES & DB AUDITING ARE FULLY OPERATIONAL!")
    else:
        print(f"  {total - passed} tests failed. Please review output above.")

if __name__ == "__main__":
    test_master()
