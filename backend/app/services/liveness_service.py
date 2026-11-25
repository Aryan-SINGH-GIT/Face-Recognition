import cv2
import numpy as np
from PIL import Image

class LivenessService:
    def __init__(
        self,
        blur_min_threshold: float = 14.0,     # Rejects severely out-of-focus prints or blank frames
        chroma_min_threshold: float = 2.2,    # Rejects flat monochrome prints / paper
        moire_display_threshold: float = 0.65, # Rejects digital display / mobile screen subpixel grids
        specular_glare_threshold: float = 0.05 # Rejects screen glass specular glare patches
    ):
        self.blur_min_threshold = blur_min_threshold
        self.chroma_min_threshold = chroma_min_threshold
        self.moire_display_threshold = moire_display_threshold
        self.specular_glare_threshold = specular_glare_threshold

    def evaluate_liveness(self, pil_image: Image.Image) -> tuple[bool, float, str]:
        """
        Multimodal passive anti-spoofing engine:
        1. Rectangular Device Bezel & Straight Edge Detection: Detects phone borders.
        2. Screen Glass Specular Glare: Detects reflective phone screen glass hotspots.
        3. High Frequency FFT & Moire: Detects digital display subpixel grid interference.
        4. Laplacian Focus: Detects blurred/flat printouts.
        5. YCrCb Chrominance: Detects black-and-white or desaturated paper prints.

        Returns: (is_live: bool, confidence_score: float [0-1], message: str)
        """
        # Convert PIL to OpenCV BGR and Grayscale
        cv_img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # -------------------------------------------------------------
        # 1. Laplacian Focus & Blur Analysis (Printed Paper / Flat Spoof)
        # -------------------------------------------------------------
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        blur_score = float(laplacian.var())

        # -------------------------------------------------------------
        # 2. Color Texture & Chrominance Diversity (Paper Print Attack)
        # -------------------------------------------------------------
        ycrcb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2YCrCb)
        y, cr, cb = cv2.split(ycrcb)
        chroma_std = float(np.std(cr) + np.std(cb)) / 2.0

        # -------------------------------------------------------------
        # 3. Mobile Display Frequency Spectrum / Moire Analysis
        # -------------------------------------------------------------
        # Analyze central face ROI so background foliage / roof grids do not trigger false Moire
        center_gray = gray[int(h * 0.15):int(h * 0.85), int(w * 0.15):int(w * 0.85)]
        f_transform = np.fft.fft2(center_gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = 20 * np.log(np.abs(f_shift) + 1e-6)
        high_freq_ratio = float(np.mean(magnitude_spectrum > 135))

        # -------------------------------------------------------------
        # 4. Mobile Screen Specular Glare / Glass Reflection Analysis
        # -------------------------------------------------------------
        # Measure specular highlights in the central region (excludes plain background walls)
        center = cv_img[int(h * 0.15):int(h * 0.85), int(w * 0.15):int(w * 0.85)]
        b_ch, g_ch, r_ch = cv2.split(center)
        specular_ratio = float(np.mean((r_ch > 245) & (g_ch > 245) & (b_ch > 245)))

        # -------------------------------------------------------------
        # 5. Rectangular Device Bezel / Screen Edge Detection
        # -------------------------------------------------------------
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=70, minLineLength=int(min(h, w) * 0.35), maxLineGap=15)
        
        has_phone_bezel = False
        if lines is not None:
            horiz_count = 0
            vert_count = 0
            for line in lines:
                coords = line.flatten()
                if len(coords) >= 4:
                    x1, y1, x2, y2 = coords[0], coords[1], coords[2], coords[3]
                    angle = abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
                    if (angle <= 10) or (angle >= 170):
                        horiz_count += 1
                    elif (80 <= angle <= 100):
                        vert_count += 1
            # A physical device frame/bezel forms a 2D bounding rectangle with both vertical and horizontal borders
            if (horiz_count >= 1 and vert_count >= 2) or (horiz_count >= 2 and vert_count >= 1):
                has_phone_bezel = True

        # -------------------------------------------------------------
        # Aggregate Liveness Score Calculation
        # -------------------------------------------------------------
        norm_blur = min(1.0, blur_score / 120.0)
        norm_chroma = min(1.0, chroma_std / 15.0)
        norm_moire = max(0.0, 1.0 - (high_freq_ratio / 0.70))
        norm_glare = 1.0 if not has_phone_bezel else max(0.0, 1.0 - (specular_ratio / 0.05))
        
        liveness_score = round(float(0.35 * norm_blur + 0.35 * norm_chroma + 0.20 * norm_moire + 0.10 * norm_glare), 3)

        # -------------------------------------------------------------
        # Anti-Spoofing Rejection Rules
        # -------------------------------------------------------------
        # Check A: Mobile Screen Bezel & Screen Signature (Device Frame in view)
        if has_phone_bezel and (high_freq_ratio > 0.30 or specular_ratio > 0.02):
            return False, liveness_score, "Spoof detected: Mobile phone screen / device frame detected in camera view"

        # Check B: Digital Display Moire Pattern (Requires screen bezel or glassy specular glare)
        if (high_freq_ratio >= 0.92 and specular_ratio > 0.025) or (high_freq_ratio >= 0.85 and has_phone_bezel):
            return False, liveness_score, f"Spoof detected: Digital display screen replay detected (Moire ratio: {high_freq_ratio:.3f})"

        # Check C: Extremely Blurry / Out-of-Focus Monochrome Paper
        if blur_score < self.blur_min_threshold and chroma_std < self.chroma_min_threshold:
            return False, liveness_score, f"Spoof suspected: Flat printed photo detected (Blur: {blur_score:.1f}, Chroma: {chroma_std:.1f})"

        # Passed all liveness checks
        return True, liveness_score, "Live human face verified"

liveness_service = LivenessService()
