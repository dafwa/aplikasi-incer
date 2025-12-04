// Variabel Global
let currentFile = null; // Menyimpan file gambar yang akan diproses
let videoStream = null;

// Elemen DOM
const imageInput = document.getElementById('imageInput');
const previewImage = document.getElementById('previewImage');
const processBtn = document.getElementById('processBtn');
const actionSelect = document.getElementById('actionSelect');
const bgInputContainer = document.getElementById('bgInputContainer');
const bgInput = document.getElementById('bgInput');
const uploadArea = document.querySelector('.upload-area'); // [BARU] Area Drag & Drop

// Elemen Webcam
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const startCameraBtn = document.getElementById('startCameraBtn');
const captureBtn = document.getElementById('captureBtn');

// ==========================================
// 1. LOGIKA DRAG & DROP & UPLOAD (TERPADU)
// ==========================================

// Mencegah default browser (agar file tidak terbuka di tab baru)
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    uploadArea.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// Visual Feedback (Ganti warna border saat file di atas kotak)
['dragenter', 'dragover'].forEach(eventName => {
    uploadArea.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    uploadArea.addEventListener(eventName, unhighlight, false);
});

function highlight(e) {
    uploadArea.classList.add('highlight');
}

function unhighlight(e) {
    uploadArea.classList.remove('highlight');
}

// Handle saat file dijatuhkan (DROP)
uploadArea.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

// Handle saat file dipilih lewat klik (INPUT CHANGE)
imageInput.addEventListener('change', function(e) {
    handleFiles(this.files);
});

// FUNGSI UTAMA PENANGANAN FILE
function handleFiles(files) {
    if (files.length > 0) {
        const file = files[0];
        
        // Validasi sederhana: Pastikan itu gambar
        if (!file.type.startsWith('image/')) {
            alert("Mohon upload file gambar saja (JPG/PNG).");
            return;
        }

        // Update variabel global
        currentFile = file;
        
        // Sinkronisasi ke input file (opsional, agar konsisten)
        // Ini berguna jika user drop file, tapi sistem validasi form mengecek input element
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        imageInput.files = dataTransfer.files;

        // Tampilkan Preview
        displayPreview(file);
        processBtn.disabled = false;
    }
}

// Helper: Menampilkan preview
function displayPreview(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        previewImage.src = e.target.result;
        previewImage.style.display = 'block';
        
        // Sembunyikan text placeholder
        const placeholder = document.getElementById('previewPlaceholder');
        if(placeholder) placeholder.style.display = 'none';
    }
    reader.readAsDataURL(file);
}

// ==========================================
// 2. LOGIKA WEBCAM
// ==========================================
startCameraBtn.addEventListener('click', async () => {
    if (videoStream) {
        stopCamera();
    } else {
        await startCamera();
    }
});

async function startCamera() {
    try {
        videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = videoStream;
        video.style.display = 'block';
        
        captureBtn.disabled = false;

        startCameraBtn.textContent = "Matikan Kamera";
        startCameraBtn.classList.remove('btn-primary');
        startCameraBtn.classList.add('btn-danger');

    } catch (err) {
        alert("Gagal mengakses kamera: " + err);
        console.error(err);
    }
}

function stopCamera() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        
        video.srcObject = null;
        videoStream = null;
        
        video.style.display = 'none';
        captureBtn.disabled = true;

        startCameraBtn.textContent = "Nyalakan Kamera";
        startCameraBtn.classList.remove('btn-danger');
        startCameraBtn.classList.add('btn-primary');
    }
}

// Matikan kamera otomatis jika user pindah ke Tab Upload
document.getElementById('upload-tab').addEventListener('click', () => {
    if (videoStream) {
        stopCamera();
    }
});

captureBtn.addEventListener('click', () => {
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Mirroring effect
    context.translate(canvas.width, 0);
    context.scale(-1, 1);

    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
        // Menggunakan handleFiles agar konsisten
        const file = new File([blob], "webcam_capture.png", { type: "image/png" });
        // Kita bungkus dalam array/list agar mirip input files
        handleFiles([file]); 
        
        // Pindah ke tab upload secara otomatis agar user melihat hasilnya (Opsional)
        // document.getElementById('upload-tab').click();
        
    }, 'image/png');
});

// ==========================================
// 3. LOGIKA UI (Replace Background Options)
// ==========================================
actionSelect.addEventListener('change', function() {
    if (this.value === 'replace_bg') {
        bgInputContainer.style.display = 'block';
    } else {
        bgInputContainer.style.display = 'none';
    }
});

const modeImage = document.getElementById('modeImage');
const modeColor = document.getElementById('modeColor');
const inputImageContainer = document.getElementById('inputImageContainer');
const inputColorContainer = document.getElementById('inputColorContainer');

modeImage.addEventListener('change', () => {
    inputImageContainer.style.display = 'block';
    inputColorContainer.style.display = 'none';
});

modeColor.addEventListener('change', () => {
    inputImageContainer.style.display = 'none';
    inputColorContainer.style.display = 'block';
});

// ==========================================
// 4. PENGIRIMAN DATA KE API (BACKEND)
// ==========================================
document.getElementById('processForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    if (!currentFile) {
        alert("Silakan pilih gambar atau ambil foto terlebih dahulu!");
        return;
    }

    const formData = new FormData();
    formData.append('file', currentFile);
    formData.append('action', actionSelect.value);

    if (actionSelect.value === 'replace_bg') {
        const isColorMode = document.getElementById('modeColor').checked;
        const bgColorInput = document.getElementById('bgColorInput');

        if (isColorMode) {
            formData.append('bg_mode', 'color');
            formData.append('bg_color_hex', bgColorInput.value);
        } else {
            if (bgInput.files.length > 0) {
                formData.append('bg_mode', 'image');
                formData.append('bg_file', bgInput.files[0]);
            } else {
                alert("Anda memilih Ganti Background Gambar, tapi belum mengupload gambar backgroundnya.");
                return;
            }
        }
    }

    processBtn.textContent = "Memproses...";
    processBtn.disabled = true;

    try {
        const response = await fetch('/api/process-image', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Terjadi kesalahan di server");
        }

        const data = await response.json();

        const resultImage = document.getElementById('resultImage');
        const downloadLink = document.getElementById('downloadLink');
        const resultCard = document.getElementById('resultCard');
        const executionTimeBadge = document.getElementById('executionTime');

        const imageDataUrl = "data:image/png;base64," + data.image_base64;

        resultImage.src = imageDataUrl;
        downloadLink.href = imageDataUrl;
        downloadLink.download = `result-${data.action}.png`;

        if (data.execution_time) {
            executionTimeBadge.textContent = data.execution_time;
        }
        
        resultCard.style.display = 'block';

    } catch (error) {
        alert("Error: " + error.message);
    } finally {
        processBtn.innerHTML = '<i class="fas fa-bolt me-2"></i>Proses Citra'; // Balikin icon
        processBtn.disabled = false;
    }
});