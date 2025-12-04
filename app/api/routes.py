from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, Tuple
import cv2
import numpy as np
import base64
import time

# Import Logic Modules
from app.services.image_processor import ImageProcessor
from app.services.segmenter import MediaPipeSegmenter

router = APIRouter()
segmenter = MediaPipeSegmenter()

# --- Helper Functions ---

def _read_image_file(file_bytes: bytes) -> np.ndarray:
    # Decodes bytes into OpenCV BGR image array.
    nparr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Could not decode image data.")
    return img

def _hex_to_bgr(hex_color: str) -> Tuple[int, int, int]:
    # Converts Hex string (e.g., '#FF0000') to BGR Tuple (0, 0, 255).
    hex_color = hex_color.lstrip('#')
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (b, g, r)  # OpenCV uses BGR order
    except (ValueError, IndexError):
        return (255, 255, 255) # Default to white on error

# --- Main Endpoint ---

@router.post("/process-image")
async def process_image(
    file: UploadFile = File(...),
    action: str = Form(...),
    bg_file: Optional[UploadFile] = File(None),
    bg_mode: Optional[str] = Form(None),      # 'image' or 'color'
    bg_color_hex: Optional[str] = Form(None)  # e.g., '#ff0000'
):
    try:
        # 1. Read Main Image (Foreground)
        contents = await file.read()
        image = _read_image_file(contents)

        processed_image = None

        # === MULAI STOPWATCH ===
        start_time = time.perf_counter()

        # 2. Process Logic
        if action == "grayscale":
            processed_image = ImageProcessor.to_grayscale(image)
        
        elif action == "blur":
            processed_image = ImageProcessor.apply_blur(image)
        
        elif action == "sepia":
            processed_image = ImageProcessor.apply_sepia(image)

        elif action == "edge_detection":
            processed_image = ImageProcessor.apply_edge_detection(image)

        elif action == "face_mesh":
            # Memanggil fungsi visualisasi landmark dari segmenter
            processed_image = segmenter.draw_face_mesh(image)

        elif action == "threshold":
            processed_image = ImageProcessor.apply_threshold(image)
        
        elif action == "remove_bg":
            # Transparent background (PNG)
            processed_image = segmenter.remove_background(image, transparent=True)
            
        elif action == "replace_bg":
            bg_image = None
            
            # Prepare Background: Color Mode
            if bg_mode == "color" and bg_color_hex:
                h, w, _ = image.shape
                # Create a solid color image with same dimensions as foreground
                bg_image = np.zeros((h, w, 3), dtype=np.uint8)
                bg_image[:] = _hex_to_bgr(bg_color_hex)
            
            # Prepare Background: Image Mode
            else:
                if not bg_file:
                    raise HTTPException(status_code=400, detail="Background file is required for image mode.")
                
                bg_contents = await bg_file.read()
                bg_image = _read_image_file(bg_contents)
            
            # Execute Replacement
            # Note: Resizing logic is now handled inside the segmenter service
            processed_image = segmenter.replace_background(image, bg_image)
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
        
        # === HENTIKAN STOPWATCH ===
        end_time = time.perf_counter()
        
        # Hitung durasi dalam milidetik (ms)
        execution_time_ms = (end_time - start_time) * 1000

        # 3. Encode Result to Base64 (In-Memory)
        # We use PNG to support transparency (Alpha channel)
        success, buffer = cv2.imencode('.png', processed_image)
        if not success:
            raise RuntimeError("Failed to encode processed image.")
            
        b64_string = base64.b64encode(buffer).decode('utf-8')

        return {
            "filename": file.filename,
            "action": action,
            "image_base64": b64_string,
            "execution_time": f"{execution_time_ms:.2f} ms" # <--- Kirim data ini ke frontend
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log error in production environment here
        print(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error during image processing.")