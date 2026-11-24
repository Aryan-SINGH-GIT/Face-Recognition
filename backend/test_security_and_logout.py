import requests
import io

BASE_URL = "http://127.0.0.1:8000"

def test_security_and_logout():
    print("=" * 65)
    print("  TESTING LOGOUT & SECURITY VULNERABILITY MITIGATIONS")
    print("=" * 65)

    # 1. Login as Admin
    print("\n[1] Testing Admin Login (POST /auth/login)...")
    res = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("    [PASS] Token issued successfully.")

    # 2. Test Authorized Admin Action using the Token
    print("\n[2] Testing Token Validity on GET /health and admin check...")
    res = requests.get(f"{BASE_URL}/health", headers=headers)
    assert res.status_code == 200
    print("    [PASS] Token is active and authorized.")

    # 3. Test Secure Logout (POST /auth/logout)
    print("\n[3] Testing Server-Side Logout (POST /auth/logout)...")
    res = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
    assert res.status_code == 200, f"Logout failed: {res.text}"
    print(f"    [PASS] Logout response: {res.json()['message']}")

    # 4. Verify Revoked Token Replay Attack is Blocked
    print("\n[4] Verifying Replay Prevention (Reusing Revoked Token on /enroll)...")
    fake_img = io.BytesIO(b"dummy image data")
    res = requests.post(
        f"{BASE_URL}/enroll",
        headers=headers,
        data={"identity_name": "Attacker_Replay"},
        files={"file": ("test.jpg", fake_img, "image/jpeg")}
    )
    assert res.status_code == 401, f"Expected 401, got {res.status_code}: {res.text}"
    print(f"    [PASS] Revoked token correctly rejected! Detail: {res.json()['detail']}")

    # 5. Test Unauthorized Admin Creation Prevention (POST /auth/register without Super Admin)
    print("\n[5] Testing Unauthorized Admin Registration Prevention...")
    res = requests.post(f"{BASE_URL}/auth/register", json={"username": "rogue_admin", "password": "password123"})
    assert res.status_code == 403, f"Expected 403, got {res.status_code}: {res.text}"
    print(f"    [PASS] Rogue registration blocked! Detail: {res.json()['detail']}")

    # 6. Test File Size Limit (Oversized payload > 10MB)
    print("\n[6] Testing File Upload Size Protection (> 10MB)...")
    huge_data = b"0" * (11 * 1024 * 1024) # 11MB
    res = requests.post(
        f"{BASE_URL}/verify",
        files={"file": ("large.jpg", io.BytesIO(huge_data), "image/jpeg")}
    )
    assert res.status_code == 413, f"Expected 413 Entity Too Large, got {res.status_code}: {res.text}"
    print(f"    [PASS] Oversized upload blocked with HTTP 413! Detail: {res.json()['detail']}")

    # 7. Test Identity Name Injection Sanitization
    print("\n[7] Testing Identity Name Sanitization (Path Traversal / Injections)...")
    fake_valid_img = io.BytesIO(b"\xff\xd8\xff\xe0" + b"0" * 100) # JPEG header dummy
    res = requests.post(
        f"{BASE_URL}/user/register",
        data={"full_name": "../../../etc/passwd"},
        files={"file": ("test.jpg", fake_valid_img, "image/jpeg")}
    )
    assert res.status_code == 400, f"Expected 400, got {res.status_code}: {res.text}"
    print(f"    [PASS] Malicious name rejected! Detail: {res.json()['detail']}")

    print("\n" + "=" * 65)
    print("  ALL LOGOUT & SECURITY VULNERABILITY TESTS PASSED (100%)!")
    print("=" * 65)

if __name__ == "__main__":
    test_security_and_logout()
