import cv2
import mediapipe as mp
import numpy as np
from typing import Tuple, Optional

class MediaPipeSegmenter:
    # Wrapper class for MediaPipe Selfie Segmentation.
    # Handles background removal and replacement logic.
    
    # Confidence threshold for determining foreground (person) vs background
    _SEGMENTATION_THRESHOLD = 0.5 
    
    def __init__(self, model_selection: int = 1):
        # Args:
        # model_selection: 0 for general/square, 1 for landscape (default).

        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
        self.segmenter = self.mp_selfie_segmentation.SelfieSegmentation(
            model_selection=model_selection
        )

        # 2. Model Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,      # True karena kita proses per gambar (bukan stream)
            max_num_faces=1,             # Fokus ke 1 wajah saja
            refine_landmarks=True,       # Lebih detail di mata dan bibir
            min_detection_confidence=0.5
        )
        
        # Utilities untuk menggambar garis
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def remove_background(
        self, 
        image: np.ndarray, 
        bg_color: Tuple[int, int, int] = (255, 255, 255), 
        transparent: bool = False
    ) -> np.ndarray:

        # Removes the background from the image.
        
        # Args:
        # image: Input image (BGR format).
        # bg_color: Tuple of (B, G, R) for solid background. Ignored if transparent=True.
        # transparent: If True, returns BGRA image with transparent background.

        if image is None:
            raise ValueError("Input image cannot be None.")

        # MediaPipe requires RGB input
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.segmenter.process(image_rgb)
        
        # Ambil raw mask (probabilitas 0.0 - 1.0)
        raw_mask = results.segmentation_mask

        # TEKNIK HYBRID: Refinement Masker (Perbaikan Tepi)
        # Kita panggil fungsi perbaikan yang menggunakan teknik klasik
        refined_mask = self._refine_mask(raw_mask)

        # Apply Mask
        if transparent:
            return self._apply_transparency(image, refined_mask)
        else:
            return self._apply_solid_background(image, refined_mask, bg_color)

    def replace_background(self, foreground: np.ndarray, background_image: np.ndarray) -> np.ndarray:

        # Replaces background with a custom image.
        # Both inputs must be valid numpy arrays.
        
        # Resize background to match foreground dimensions (width, height)
        # foreground.shape is (Height, Width, Channels)
        target_size = (foreground.shape[1], foreground.shape[0])
        
        # Only resize if dimensions differ to save processing time
        if (background_image.shape[1], background_image.shape[0]) != target_size:
            background_image = cv2.resize(background_image, target_size)

        # Process segmentation
        image_rgb = cv2.cvtColor(foreground, cv2.COLOR_BGR2RGB)
        results = self.segmenter.process(image_rgb)
        
        # --- HYBRID REFINEMENT ---
        raw_mask = results.segmentation_mask
        refined_mask = self._refine_mask(raw_mask)
        # -------------------------
        
        # Gunakan refined_mask untuk menggabungkan
        # Kita perlu expand dimensi mask agar jadi 3 channel (H, W, 3)
        mask_3d = np.stack((refined_mask,) * 3, axis=-1)
        
        # Lakukan Linear Interpolation (Blending Halus)
        # Rumus: (Foreground * Alpha) + (Background * (1 - Alpha))
        # Ini lebih halus daripada np.where (Hard Cut)
        output_image = (foreground * mask_3d + background_image * (1 - mask_3d)).astype(np.uint8)
        
        return output_image
    
    def draw_face_mesh(self, image: np.ndarray) -> np.ndarray:

        # Menggambar jaring-jaring (landmarks) wajah di atas citra asli.
        if image is None:
            raise ValueError("Input image cannot be None.")

        # Copy image agar gambar asli tidak rusak (opsional, tapi good practice)
        annotated_image = image.copy()

        # Konversi ke RGB
        image_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
        
        # Proses deteksi landmark
        results = self.face_mesh.process(image_rgb)

        # Jika ada wajah terdeteksi
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                
                # 1. Gambar Jaring-jaring (Tesselation)
                self.mp_drawing.draw_landmarks(
                    image=annotated_image,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_tesselation_style()
                )
                
                # 2. Gambar Kontur Wajah (Mata, Alis, Bibir, Garis Wajah)
                self.mp_drawing.draw_landmarks(
                    image=annotated_image,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_contours_style()
                )
        
        return annotated_image
    
    def _refine_mask(self, raw_mask: np.ndarray) -> np.ndarray:
        
        # Menggabungkan output AI dengan operasi morfologi klasik untuk hasil lebih rapi.
        # 1. Thresholding (Binarisasi Awal)
        # Kita buat batas tegas dulu: > 0.5 jadi 1, sisanya 0
        mask = (raw_mask > self._SEGMENTATION_THRESHOLD).astype(np.float32)

        # 2. Morphological Operation (Closing)
        # Berguna untuk menutup lubang-lubang kecil di dalam objek (misal: logo baju)
        # Kernel 3x3 adalah "jendela" pengamatan
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # 3. Gaussian Blur (Feathering/Soft Edges)
        # Ini yang paling penting! Membuat pinggiran tidak tajam (anti-aliasing)
        # Sigma (2.0) menentukan seberapa lebar keburamannya
        mask = cv2.GaussianBlur(mask, (0, 0), sigmaX=2.0, sigmaY=2.0)
        
        return mask

    def _apply_transparency(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        # Ubah mask (0.0 - 1.0) menjadi Alpha (0 - 255)
        alpha_channel = (mask * 255).astype(np.uint8)
        return np.dstack((image, alpha_channel))

    def _apply_solid_background(self, image: np.ndarray, mask: np.ndarray, color: Tuple[int, int, int]) -> np.ndarray:
        bg_image = np.zeros(image.shape, dtype=np.uint8)
        bg_image[:] = color
        
        # Blending Halus
        mask_3d = np.stack((mask,) * 3, axis=-1)
        
        # Rumus Blending: Image*Mask + BG*(1-Mask)
        output = (image * mask_3d + bg_image * (1 - mask_3d)).astype(np.uint8)
        return output