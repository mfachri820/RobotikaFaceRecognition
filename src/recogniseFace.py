import cv2
import numpy as np
import insightface
import os
import time
import requests
import soundfile as sf
import sounddevice as sd
from dotenv import load_dotenv

# === Load .env if available ===
load_dotenv()
API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"   # Default ElevenLabs voice
MODEL_ID = "eleven_flash_v2_5"      # Fastest & cheapest model

# === ElevenLabs text-to-speech ===
def speak(text):
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers = {
            "xi-api-key": API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "model_id": MODEL_ID,
            "text": text,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"⚠️ ElevenLabs API error: {response.status_code} {response.text}")
            return

        # Save and play audio
        with open("temp.wav", "wb") as f:
            f.write(response.content)
        data, sr = sf.read("temp.wav")
        sd.play(data, sr)
        sd.wait()
    except Exception as e:
        print(f"Error in TTS: {e}")

# === Load InsightFace model ===
model = insightface.app.FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
model.prepare(ctx_id=0, det_size=(640, 640))

# === Load known faces ===
dataset_folder = "dataset"
if not os.path.exists(dataset_folder):
    print(f"⚠️ Folder '{dataset_folder}' not found.")
    exit()

known_faces = {}
for file in os.listdir(dataset_folder):
    if file.endswith(".npy"):
        name = os.path.splitext(file)[0]
        path = os.path.join(dataset_folder, file)
        known_faces[name] = np.load(path)
        print(f"✅ Loaded {file} from dataset/")

if not known_faces:
    print("⚠️ No .npy files found in dataset/. Please run register_face.py first.")
    exit()

# === Helper functions ===
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def identify_face(embedding, database, threshold=0.35):
    best_match = None
    highest_score = threshold
    for name, emb in database.items():
        score = cosine_similarity(embedding, emb)
        if score > highest_score:
            best_match = name
            highest_score = score
    return best_match

# === Start webcam ===
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Could not open webcam.")
    exit()

print("🎬 Face recognition running. Press 'H' to say hello or 'Q' to quit.")

last_name = "Unknown"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    faces = model.get(frame)

    if faces:
        for face in faces:
            box = face.bbox.astype(int)
            name = identify_face(face.embedding, known_faces) or "Unknown"
            last_name = name
            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0,255,0), 2)
            cv2.putText(frame, name, (box[0], box[1]-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
    else:
        # keep showing last recognized name if no face detected
        name = last_name

    cv2.imshow("InsightFace Recognition + ElevenLabs Voice", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('h'):
        if last_name != "Unknown":
            speak(f"Hello, {last_name}")
        else:
            speak("Hello there")

cap.release()
cv2.destroyAllWindows()
