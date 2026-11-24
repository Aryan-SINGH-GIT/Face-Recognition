import requests
from pathlib import Path
from PIL import Image
import numpy as np
import io

BASE_URL = "http://127.0.0.1:8000"

def test_duplicate_prevention_and_spoof():
    print("=" * 65)
    print("  TESTING BIOMETRIC DUPLICATE PREVENTION & ANTI-SPOOFING")
    print("=" * 65)

    dataset_dir = Path(r"c:\D\face_recogonation\ml\dataset atelier 4")
    sample_img = dataset_dir / "Jimmy_Carter" / "Jimmy_Carter_0001.jpg"
    assert sample_img.exists()

    # -------------------------------------------------------------
    # 1. Test Duplicate Registration Under DIFFERENT Name
    # -------------------------------------------------------------
    print("\n[1] Testing duplicate face registration under DIFFERENT name...")
    with open(sample_img, "rb") as f:
        res = requests.post(
            f"{BASE_URL}/user/register",
            data={"full_name": "Jimmy_Imposter_Clone", "display_name": "Clone"},
            files={"file": ("face.jpg", f, "image/jpeg")}
        )
    print(f"    Status: {res.status_code}")
    print(f"    Detail: {res.json().get('detail')}")
    assert res.status_code == 409, f"Expected 409 Conflict, got {res.status_code}"
    assert "Biometric duplicate" in res.json().get("detail", "")
    print("    [PASS] Duplicate face under different name was blocked!")

    # -------------------------------------------------------------
    # 2. Test Duplicate Registration Under SAME Name
    # -------------------------------------------------------------
    print("\n[2] Testing duplicate face registration under SAME name...")
    with open(sample_img, "rb") as f:
        res = requests.post(
            f"{BASE_URL}/user/register",
            data={"full_name": "Jimmy_Carter", "display_name": "Jimmy"},
            files={"file": ("face.jpg", f, "image/jpeg")}
        )
    print(f"    Status: {res.status_code}")
    print(f"    Detail: {res.json().get('detail')}")
    assert res.status_code == 409, f"Expected 409 Conflict, got {res.status_code}"
    print("    [PASS] Re-registering existing identity was blocked!")

    # -------------------------------------------------------------
    # 3. Test Mobile Display Replay Spoofing Detection
    # -------------------------------------------------------------
    print("\n[3] Testing Screen Replay / Mobile Spoofing Detection...")
    # Simulate a mobile screen replay attack:
    # A real face captured with LCD/OLED subpixel grid + screen borders + specular screen glare
    orig = Image.open(sample_img).convert("RGB")
    arr = np.array(orig).copy()
    h, w, c = arr.shape

    # Add mobile phone rectangular border / bezel
    arr[0:15, :] = [20, 20, 20]     # Top phone bezel
    arr[-15:, :] = [20, 20, 20]    # Bottom phone bezel
    arr[:, 0:15] = [20, 20, 20]     # Left phone bezel
    arr[:, -15:] = [20, 20, 20]    # Right phone bezel

    # Add screen glass reflection glare hotspot (saturated glass reflection)
    arr[20:45, 20:55] = [255, 255, 255]

    # Add subpixel LCD stripe noise (moire grid)
    arr[:, ::2, 2] = np.clip(arr[:, ::2, 2] * 1.3, 0, 255) # Blue subpixel stripe boost

    spoof_buf = io.BytesIO()
    Image.fromarray(arr).save(spoof_buf, format="JPEG", quality=95)
    spoof_bytes = spoof_buf.getvalue()

    res = requests.post(
        f"{BASE_URL}/user/login",
        files={"file": ("spoof_screen.jpg", io.BytesIO(spoof_bytes), "image/jpeg")}
    )
    print(f"    Status Code: {res.status_code}")
    data = res.json()
    print(f"    Access Granted: {data.get('granted')}")
    print(f"    Liveness Status: {data.get('status')}")
    print(f"    Server Message: {data.get('message')}")

    assert data.get("granted") is False, "Expected spoof attack to be denied!"
    assert data.get("status") == "SPOOF_DETECTED", f"Expected SPOOF_DETECTED, got {data.get('status')}"
    print("    [PASS] Mobile screen spoof attack was successfully detected and rejected!")

    print("\n" + "=" * 65)
    print("  ALL BIOMETRIC DE-DUPLICATION & SPOOF TESTS PASSED (100%)!")
    print("=" * 65)

if __name__ == "__main__":
    test_duplicate_prevention_and_spoof()
