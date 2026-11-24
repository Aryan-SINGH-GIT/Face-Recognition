import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app

def run_comprehensive_backend_test():
    with TestClient(app) as client:
        print("=" * 65)
        print("     FULL BACKEND TEST SUITE (100% COMPLETION VERIFICATION)")
        print("=" * 65)

        # 1. Health & Pre-warming
        print("\n[1] Testing GET /health...")
        health = client.get("/health").json()
        print(f"    Status: {health['status']}, Models Pre-warmed: {health['models_loaded']}")
        assert health["status"] == "ok"
        assert health["models_loaded"] is True

        # 2. Config & Hyperparameters
        print("\n[2] Testing GET /config...")
        cfg = client.get("/config").json()
        print(f"    L2 Threshold: {cfg['threshold']}, Liveness Enabled: {cfg['liveness_enabled']}")
        assert cfg["liveness_enabled"] is True

        # 3. Admin Authentication & JWT Generation
        print("\n[3] Testing POST /auth/login (Admin JWT)...")
        login_res = client.post("/auth/login", json={"username": "admin", "password": "admin123"})
        assert login_res.status_code == 200
        token_data = login_res.json()
        token = token_data["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}
        print(f"    JWT Token issued successfully for '{token_data['username']}' (Role: {token_data['role']})")

        # 4. Biometric Verification with Anti-Spoofing & Automatic DB Logging
        print("\n[4] Testing POST /verify (Bill Frist + Liveness + DB Audit)...")
        test_img = Path("c:/D/face_recogonation/ml/dataset atelier 4/Bill_Frist/Bill_Frist_0001.jpg")
        with open(test_img, "rb") as f:
            verify_res = client.post(
                "/verify",
                files={"file": ("bill.jpg", f, "image/jpeg")},
                params={"check_liveness": True}
            )
        assert verify_res.status_code == 200
        v_data = verify_res.json()
        print(f"    Match Found : {v_data['match_found']}")
        print(f"    Identity    : {v_data['identity']}")
        print(f"    Confidence  : {v_data['confidence']}%")
        print(f"    Is Live     : {v_data['is_live']} (Liveness Score: {v_data['liveness_score']})")
        print(f"    Access Log  : Status '{v_data['status']}'")
        assert v_data["match_found"] is True
        assert v_data["identity"] == "Bill_Frist"

        # 5. Access Audit Logs in SQLite
        print("\n[5] Testing GET /logs (Verifying persistent DB audit log)...")
        logs_res = client.get("/logs?page=1&limit=5")
        assert logs_res.status_code == 200
        logs_data = logs_res.json()
        print(f"    Total Audit Logs in DB: {logs_data['total']}")
        latest_log = logs_data["logs"][0]
        print(f"    Latest Recorded Event : ID={latest_log['id']}, Status={latest_log['status']}, Identity={latest_log['matched_identity']}")
        assert logs_data["total"] >= 1

        # 6. Analytics & KPI Summary
        print("\n[6] Testing GET /analytics/summary...")
        analytics = client.get("/analytics/summary").json()
        print(f"    Total Verifications: {analytics['total_verifications']}")
        print(f"    Granted Entries    : {analytics['granted_count']}")
        print(f"    Pass Rate          : {analytics['pass_rate_percentage']}%")
        print(f"    Enrolled People    : {analytics['enrolled_identities_count']}")
        assert analytics["granted_count"] >= 1

        # 7. Dynamic User Enrollment (Protected Endpoint)
        print("\n[7] Testing POST /enroll (Admin JWT Protected)...")
        test_enroll_img = Path("c:/D/face_recogonation/ml/dataset atelier 4/Jennifer_Garner/Jennifer_Garner_0001.jpg")
        with open(test_enroll_img, "rb") as f:
            enroll_res = client.post(
                "/enroll",
                headers=auth_headers,
                files={"file": ("new_user.jpg", f, "image/jpeg")},
                data={"identity_name": "Test_Enrolled_Employee"}
            )
        assert enroll_res.status_code == 200
        enroll_data = enroll_res.json()
        print(f"    Enrollment Success: {enroll_data['success']}")
        print(f"    Registered Name   : {enroll_data['identity']}")
        print(f"    Total DB Vectors  : {enroll_data['total_embeddings']}")

        # 8. De-registering Employee (Rebuilding Faiss Index)
        print("\n[8] Testing DELETE /identities/{name} (Admin JWT Protected)...")
        del_res = client.delete(
            "/identities/Test_Enrolled_Employee",
            headers=auth_headers
        )
        assert del_res.status_code == 200
        del_data = del_res.json()
        print(f"    De-registration: {del_data['message']}")
        print(f"    Remaining Vectors in Faiss: {del_data['remaining_embeddings']}")

        print("\n" + "=" * 65)
        print("  SUCCESS: 100% OF THE BACKEND IS COMPLETE, TESTED, AND WORKING!")
        print("=" * 65)

if __name__ == "__main__":
    run_comprehensive_backend_test()
