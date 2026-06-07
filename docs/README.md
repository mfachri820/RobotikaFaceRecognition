# 📘 **Face Recognition & Smart Follower Robot — README (Simple User Guide)**

## 📌 **Deskripsi Singkat**

Proyek ini terdiri dari beberapa modul yang bekerja sama untuk:

1. **Mendaftarkan wajah pengguna**
2. **Mengenali wajah menggunakan InsightFace**
3. **Memberikan respon suara menggunakan ElevenLabs**
4. **Mengontrol robot (Arduino)** untuk *follow target user*
5. **Debugging kamera** untuk memastikan webcam bekerja stabil

Program ditulis menggunakan **Python**, **OpenCV**, **InsightFace**, dan **Arduino (serial commands)**.

---

# 📂 **Struktur Folder**

```
Proyek/
├── src/                          # Semua script Python
│   ├── registerFace.py           # Mendaftarkan wajah & menyimpan embedding (.npy)
│   ├── recogniseFace.py          # Deteksi wajah + ucapan suara ElevenLabs
│   ├── smart-follower.py         # Robot mengikuti target user via webcam
│   ├── smart-recognise-mobile.py # Robot mengikuti target user via kamera HP (IP Webcam)
│   ├── camera_debug.py           # Debug dan perbaikan masalah kamera
│   └── test.py                   # Script testing
├── arduino/                      # Program Arduino
│   └── code-arduino.ino          # Kontrol motor via serial commands
├── dataset/                      # Data wajah (.npy embeddings)
├── docs/                         # Dokumentasi
│   └── README.md                 # File ini
└── .env                          # API key ElevenLabs (ELEVEN_API_KEY)
```

---

# 🛠 **1. Instalasi & Persiapan**

### **A. Install dependency Python**

```bash
pip install opencv-python insightface python-dotenv sounddevice soundfile requests numpy pyserial
```

### **B. Buat folder dataset**

Pastikan ada folder:

```
dataset/
```

Di dalamnya akan tersimpan file-file `.npy` sebagai data wajah.

### **C. Isi file `.env`**

```
ELEVEN_API_KEY=your_api_key_here
```

(berdasarkan isi file kamu )

---

# 🧍‍♂️ **2. Register Wajah**

Jalankan:

```bash
python src/registerFace.py
```



### Cara kerja:

1. Kamera menyala
2. Tekan **SPACE** untuk capture wajah
3. Masukkan nama (misal: `fachri`)
4. File `fachri.npy` akan tersimpan di folder `dataset/`

---

# 👁️ **3. Face Recognition + Voice**

Jalankan:

```bash
python src/recogniseFace.py
```



### Fitur:

* Deteksi wajah real-time
* Menampilkan bounding box dan nama
* Tekan **H** untuk menyapa dengan suara ElevenLabs
* Tekan **Q** untuk keluar

---

# 🤖 **4. Smart Robot Follower (Webcam)**

Jalankan:

```bash
python src/smart-follower.py
```



### Cara kerja:

1. Masukkan nama target (harus sama dengan file `.npy`)
2. Kamera mendeteksi wajah target
3. Arduino menerima command:

   * `L` → belok kiri
   * `R` → belok kanan
   * `F` → maju
   * `S` → berhenti

### Requirements:

* Arduino terhubung via COM port
* Webcam bekerja (debug via `src/camera_debug.py`)

---

# 📱 **5. Smart Follower (Kamera HP / IP Webcam)**

Jalankan:

```bash
python src/smart-recognise-mobile.py
```



### Set IP Webcam

Edit:

```python
ANDROID_IP = "http://<ip_kamera>:8080/video"
```

### Fungsi:

* Robot mengikuti target user melalui kamera HP
* Bisa menyapa target via ElevenLabs

---

# 🛠 **6. Debug Kamera**

Jalankan:

```bash
python src/camera_debug.py
```



### Fitur:

* Scan index kamera
* Fix masalah driver Logitech C525 (MJPG, YUY2)
* Menampilkan preview kamera
* Menyelesaikan error OpenCV highgui di Windows

---

# ⚙️ **7. Program Arduino**

File `arduino/code-arduino.ino` (tidak tampil isinya, tapi program Python mengirim command seperti:
`L`, `R`, `F`, `S`).
Arduino harus membaca serial dan menjalankan motor sesuai perintah tersebut.

---

# ▶️ **Cara Menjalankan Semua Modul**

Urutan yang disarankan:

1. **Debug webcam** → `python src/camera_debug.py`
2. **Register wajah** → `python src/registerFace.py`
3. **Test face recognition + suara** → `python src/recogniseFace.py`
4. **Test robot follower (webcam)** → `python src/smart-follower.py`
5. **(Opsional) Gunakan kamera HP** → `python src/smart-recognise-mobile.py`

---

# 🧩 **Troubleshooting**

### **Camera tidak memberi frame**

Gunakan:

```
python src/camera_debug.py
```

### **Arduino tidak terdeteksi**

* Cek COM port di Device Manager
* Sesuaikan variabel `SERIAL_PORT` di program Python

### **Tidak ada file .npy**

Jalankan `registerFace.py`

### **Voice ElevenLabs tidak keluar**

* Pastikan file `.env` benar
* Cek internet dan API key