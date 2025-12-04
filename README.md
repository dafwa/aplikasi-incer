# Pengembangan Aplikasi Pengolahan Citra Berbasis FastAPI & MediaPipe

**Kontributor:** Daffa Fakhir dan Muh Akhlatul Ihsan A  

**Mata Kuliah:** Instrumentasi Cerdas  

**Universitas:** Universitas Negeri Makassar

---

## Deskripsi Proyek
Aplikasi berbasis web ini dikembangkan untuk melakukan pengolahan citra digital dan segmentasi wajah secara *real-time*. Aplikasi ini memanfaatkan performa [**FastAPI**](https://fastapi.tiangolo.com/) sebagai backend dan Model Machine Learning dari [**MediaPipe**](https://pypi.org/project/mediapipe/) untuk memisahkan objek manusia dari latar belakang (*background*).

Sistem dirancang dengan efisiensi tinggi menggunakan *In-Memory Processing*, sehingga tidak membebani penyimpanan server dengan file sementara.

## Fitur Utama

### 1. Sumber Citra Fleksibel
* **Upload File**: Mendukung format gambar umum (JPG, PNG).
* **Webcam Integrasi**: Pengambilan gambar langsung dari kamera perangkat dengan fitur *toggle* (Nyalakan/Matikan) dan preview *mirrored* (seperti bercermin).

### 2. Pengolahan Citra Digital (Classical Processing)
Fitur-fitur ini menggunakan manipulasi matriks dan algoritma pengolahan citra klasik untuk analisis struktur dan warna.

* **Grayscale**: Konversi citra warna (RGB) menjadi derajat keabuan (Luminance).
* **Gaussian Blur**: Teknik penghalusan citra (*smoothing*) untuk mereduksi *noise*.
* **Sepia Filter**: Transformasi matriks warna untuk memberikan efek hangat/klasik sekaligus demonstrasi aljabar linear pada citra.
* **Canny Edge Detection**: Algoritma deteksi tepi multi-tahap untuk mengekstrak struktur dan garis batas objek dalam citra.
* **Otsu Thresholding**: Teknik binarisasi otomatis yang memisahkan objek (foreground) dan latar (background) menjadi hitam-putih mutlak berdasarkan histogram.

### 3. Computer Vision & AI (Advanced)
Fitur-fitur ini memanfaatkan model *Machine Learning* (MediaPipe) untuk pemahaman konteks visual yang lebih kompleks.

* **Face Mesh Visualization**: Memetakan dan memvisualisasikan **468 titik koordinat (landmarks)** geometri pada wajah secara *real-time* untuk analisis biometrik.
* **Hapus Background (Transparent)**: Menggunakan model *Selfie Segmentation* untuk menghapus latar belakang dan menghasilkan format **PNG Transparan** (Alpha Channel), bukan sekadar layar putih.
* **Ganti Background**: Memungkinkan penggabungan (*masking*) antara objek manusia (foreground) dengan gambar latar pilihan pengguna.

### 4. Monitoring Performa
* **Latency Counter**: Menampilkan waktu eksekusi (*execution time*) setiap algoritma dalam satuan **milidetik (ms)** untuk mengukur efisiensi sistem secara kuantitatif.

### 5. Efisiensi Sistem
* **Tanpa Temporary Files**: Hasil pengolahan citra dikirim langsung ke antarmuka pengguna menggunakan format **Base64**, menjaga kebersihan dan privasi server.
* **Download Instan**: Hasil olahan dapat langsung diunduh oleh pengguna.

---

## Teknologi yang Digunakan

* **Backend Framework**: FastAPI (Python)
* **Computer Vision**: OpenCV, MediaPipe, NumPy
* **Server**: Uvicorn
* **Frontend**: HTML5, Bootstrap 5, Vanilla JavaScript

---

## Struktur Direktori

```text
aplikasi-incer/
│
├── app/
│   ├── api/
│   │   └── routes.py           # Endpoint API (Logika Routing)
│   ├── services/
│   │   ├── image_processor.py  # Modul OpenCV Dasar
│   │   └── segmenter.py        # Modul MediaPipe (AI)
│   ├── static/
│   │   ├── css/                    # Styling Tambahan
│   │   └── js/                     # Logika Webcam & AJAX
│   ├── templates/
│   │   └── index.html          # Antarmuka Pengguna
│   └── main.py                 # Konfigurasi Utama Server
│
├── requirements.txt            # Daftar Pustaka Python
└── README.md                   # Dokumentasi Proyek
```

## INSTALASI
Silahkan Clone Repository ini
```bash
git clone https://github.com/dafwa/aplikasi-incer.git
```

Pastikan anda berada didalam ```~aplikasi-incer/```
```bash
cd aplikasi-incer
```

Buat Virtual Environment di Python atau Conda.
```bash
python -m venv [name_virtual_environment]

# jika memakai conda
conda create -n [name_virtual_environment] python=3.10
```

Setelah Virtual Environment terbuat, Aktifkan Environment.
```bash
[name_virtual_environment]/Scripts/activate

# jika memakai conda
conda activate [name_virtual_environment]
```

Download library dari ```requirements.txt```
```bash
pip install -r requirements.txt
```
atau Download Manual, lakukan ```pip install [library]```
```text
fastapi
uvicorn[standard]
python-multipart
numpy
opencv-python
mediapipe
```

## 🚀 Jalankan
Jalankan Aplikasi dengan command berikut.
```bash
uvicorn app.main:app --reload
```
