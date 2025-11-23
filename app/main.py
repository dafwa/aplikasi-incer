from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn

# Import router dari modul api
from app.api import routes

# --- Konfigurasi Path (Modern Way using pathlib) ---
# Mengambil direktori di mana file main.py ini berada
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# --- Inisialisasi Aplikasi ---
app = FastAPI(
    title="Instrumentasi Cerdas API",
    description="Sistem Pengolahan Citra & Segmentasi Wajah Berbasis MediaPipe",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url=None     # Disable ReDoc (agar lebih bersih)
)

# --- Mounting Static Files ---
# Memastikan direktori static ada agar tidak error saat startup
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# --- Template Engine Setup ---
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# --- Register Routes ---
# Menambahkan tags=["Processing"] agar rapi di dokumentasi Swagger
app.include_router(routes.router, prefix="/api", tags=["Image Processing"])

# --- Endpoints ---

@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
async def read_root(request: Request):
    # Halaman Utama (Dashboard) Aplikasi.
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health", tags=["System"])
async def health_check():
    # Endpoint untuk mengecek status kesehatan server (Health Check).
    return {
        "status": "active",
        "service": "Instrumentasi Cerdas Image Processor",
        "message": "Halo Daffa!."
    }

# --- Entry Point ---
if __name__ == "__main__":
    # Menjalankan server menggunakan Uvicorn
    # reload=True hanya digunakan saat development
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)