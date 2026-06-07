# 🤖 Face Recognition & Smart Follower Robot

Proyek robot pengikut wajah menggunakan **Python**, **OpenCV**, **InsightFace**, dan **Arduino**.

📖 **Dokumentasi lengkap**: [docs/README.md](docs/README.md)

## 📂 Struktur Folder

```
Proyek/
├── src/            # Script Python (face recognition, robot follower, dll.)
├── arduino/        # Program Arduino (kontrol motor)
├── dataset/        # Data wajah (.npy embeddings)
├── docs/           # Dokumentasi
└── .env            # API key ElevenLabs
```

## ▶️ Quick Start

```bash
# 1. Install dependencies
pip install opencv-python insightface python-dotenv sounddevice soundfile requests numpy pyserial

# 2. Isi .env dengan API key
echo ELEVEN_API_KEY=your_api_key_here > .env

# 3. Jalankan modul (dari folder root)
python src/registerFace.py          # Daftarkan wajah
python src/recogniseFace.py         # Test face recognition
python src/smart-follower.py        # Robot follower via webcam
python src/smart-recognise-mobile.py # Robot follower via kamera HP
```
