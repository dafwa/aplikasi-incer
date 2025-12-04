import cv2
import numpy as np
from typing import Optional

class ImageProcessor:
    # Utility class for basic image processing operations using OpenCV.
    # Stateless implementation using static methods.

    # Konstanta untuk matriks filter (Pre-defined kernels)
    _SEPIA_KERNEL = np.array([
        [0.272, 0.534, 0.131],
        [0.349, 0.686, 0.168],
        [0.393, 0.769, 0.189]
    ])

    @staticmethod
    def _validate_image(image: np.ndarray) -> None:
        # Internal helper to ensure image is valid.
        if image is None or image.size == 0:
            raise ValueError("Input image is empty or invalid.")

    @classmethod
    def to_grayscale(cls, image: np.ndarray) -> np.ndarray:
        cls._validate_image(image)
        try:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        except cv2.error as e:
            raise RuntimeError(f"OpenCV grayscale conversion failed: {e}")

    @classmethod
    def apply_blur(cls, image: np.ndarray, kernel_size: int = 15) -> np.ndarray:
        cls._validate_image(image)
        
        # Ensure kernel size is always odd
        k_size = kernel_size if kernel_size % 2 != 0 else kernel_size + 1
        
        return cv2.GaussianBlur(image, (k_size, k_size), 0)

    @classmethod
    def apply_sepia(cls, image: np.ndarray) -> np.ndarray:
        cls._validate_image(image)
        
        # Apply matrix transformation
        sepia_img = cv2.transform(image, cls._SEPIA_KERNEL)
        
        # Normalize and clip values to valid byte range [0-255]
        sepia_img = np.clip(sepia_img, 0, 255)
        
        return sepia_img.astype(np.uint8)
    
    @classmethod
    def apply_edge_detection(cls, image: np.ndarray) -> np.ndarray:
        cls._validate_image(image)
        
        # 1. Ubah ke Grayscale (Canny butuh 1 channel)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 2. Blur sedikit untuk hilangkan noise agar garis lebih halus
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 3. Apply Canny Algorithm
        # Threshold 1 (50): Batas bawah (dianggap tepi jika terhubung dengan tepi kuat)
        # Threshold 2 (150): Batas atas (pasti dianggap tepi)
        edges = cv2.Canny(blurred, 50, 150)
        
        # 4. Kembalikan ke format BGR agar konsisten saat di-encode/display
        # (Meski visualnya tetap hitam-putih)
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        return edges_bgr
    
    @classmethod
    def apply_threshold(cls, image: np.ndarray) -> np.ndarray:
        cls._validate_image(image)
        
        # 1. Ubah ke Grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 2. Terapkan Otsu's Thresholding
        # Parameter 0 diabaikan karena kita pakai flag THRESH_OTSU
        # Fungsi ini mengembalikan 2 nilai: (nilai_threshold_yg_didapat, citra_hasil)
        otsu_val, thresh_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # (Opsional) Print nilai threshold yang ditemukan algortima ke terminal
        print(f"Otsu's Threshold Value found: {otsu_val}")
        
        # 3. Kembalikan ke format BGR (agar bisa ditampilkan browser)
        return cv2.cvtColor(thresh_img, cv2.COLOR_GRAY2BGR)