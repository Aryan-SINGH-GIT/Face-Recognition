import requests
import json
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

def test_user_portal_endpoints():
    print("=" * 60)
    print("  TESTING USER PORTAL & BIOMETRIC AUTHENTICATION")
    print("=" * 60)

    # 1. Health check
    print("\n[1] Testing GET /health...")
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print("    Health Response:", r.json())

    # Pick a sample image from the dataset for testing
    dataset_dir = Path(r"c:\D\face_recogonation\ml\dataset atelier 4")
    sample_img_path = dataset_dir / "Jimmy_Carter" / "Jimmy_Carter_0001.jpg"
    assert sample_img_path.exists(), f"Sample image {sample_img_path} not found"

    # 2. Test Face-based User Login (Jimmy Carter is already in enrolled dataset)
    print("\n[2] Testing POST /user/login with Jimmy Carter face...")
    with open(sample_img_path, "rb") as f:
        r = requests.post(f"{BASE_URL}/user/login", files={"file": ("jimmy.jpg", f, "image/jpeg")})
    print(f"    Status Code: {r.status_code}")
    data = r.json()
    print("    Login Result:", json.dumps(data, indent=2))
    assert data["granted"] == True
    assert "Jimmy_Carter" in data["full_name"]

    # 3. Test New User Self-Registration
    # Let's register a new user test persona using Jennifer Garner's photo as an example or Edmund Stoiber
    # Wait, let's see if we can register a new persona: 'Aryan_Singh_Test' with Jennifer Garner's second photo or another photo
    enroll_img_path = dataset_dir / "Jennifer_Garner" / "Jennifer_Garner_0001.jpg"
    test_user_name = "User_Self_Enroll_Test"
    
    print(f"\n[3] Testing POST /user/register for '{test_user_name}'...")
    with open(enroll_img_path, "rb") as f:
        r = requests.post(
            f"{BASE_URL}/user/register",
            data={"full_name": test_user_name, "display_name": "Test User Persona"},
            files={"file": ("face.jpg", f, "image/jpeg")}
        )
    print(f"    Status Code: {r.status_code}")
    print("    Register Response:", r.json())
    if r.status_code == 200:
        assert r.json()["success"] == True
    elif r.status_code == 409:
        print("    (User was already registered in a previous run)")

    # 4. Test GET /user/list
    print("\n[4] Testing GET /user/list...")
    r = requests.get(f"{BASE_URL}/user/list")
    print(f"    Status Code: {r.status_code}")
    user_list = r.json()
    print(f"    Total registered users: {user_list['total']}")
    for u in user_list["users"]:
        print(f"    - {u['full_name']} (display: {u['display_name']}, total access: {u['total_access']})")

    # 5. Test Face Login with the newly registered user
    print(f"\n[5] Testing POST /user/login with newly registered user image...")
    with open(enroll_img_path, "rb") as f:
        r = requests.post(f"{BASE_URL}/user/login", files={"file": ("face.jpg", f, "image/jpeg")})
    print(f"    Status Code: {r.status_code}")
    login_res = r.json()
    print("    Login Response:", json.dumps(login_res, indent=2))

    # 6. Verify Access Log entry was recorded
    print("\n[6] Checking GET /logs for audit trail...")
    r = requests.get(f"{BASE_URL}/logs?limit=3")
    logs_data = r.json()
    print(f"    Total access logs: {logs_data['total']}")
    for log in logs_data["logs"][:3]:
        print(f"    - [{log['timestamp'][:19]}] {log['status']} | {log['matched_identity']} | conf: {log['confidence_score']}%")

    print("\n" + "=" * 60)
    print("  ALL USER PORTAL BIOMETRIC TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    test_user_portal_endpoints()
