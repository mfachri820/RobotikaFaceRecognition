import cv2
import numpy as np
import insightface
import os
import time
import serial
import serial.tools.list_ports
import requests
import soundfile as sf
import sounddevice as sd
from dotenv import load_dotenv

# === 1. SETUP & CONFIGURATION ===
load_dotenv()

# Serial / Arduino Config
SERIAL_PORT = 'COM15'  # Ensure this matches your port
BAUD_RATE = 9600

# Robot Movement Config
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
CENTER_ZONE = 100       # Deadzone in the center
STOP_WIDTH = 110        # Face width to stop

# ElevenLabs Config
API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"
MODEL_ID = "eleven_flash_v2_5"

# Android Camera Config
# REPLACE with the IP shown in your IP Webcam app
ANDROID_IP = "http://10.92.54.159:8080/video" 

# === 2. CONNECT TO ARDUINO ===
arduino = None
try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(f"✅ Connected to Arduino on {SERIAL_PORT}")
except:
    print(f"⚠️ Connection Error. Checking ports...")
    ports = serial.tools.list_ports.comports()
    for p in ports: print(f"   Found: {p.device}")
    print("⚠️ Robot running in VISION ONLY mode.")

def send_cmd(command):
    if arduino:
        arduino.write(command.encode())

# === 3. VOICE & RECOGNITION FUNCTIONS ===
def speak(text):
    """Non-blocking TTS via ElevenLabs"""
    if not API_KEY: return
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers = {"xi-api-key": API_KEY, "Content-Type": "application/json"}
        payload = {
            "model_id": MODEL_ID, 
            "text": text, 
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            with open("temp.wav", "wb") as f: f.write(response.content)
            data, sr = sf.read("temp.wav")
            sd.play(data, sr)
    except Exception as e:
        print(f"TTS Error: {e}")

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def identify_face(embedding, database, threshold=0.45):
    best_match = None
    highest_score = threshold
    for name, emb in database.items():
        score = cosine_similarity(embedding, emb)
        if score > highest_score:
            best_match = name
            highest_score = score
    return best_match

# === 4. INITIALIZATION ===
print("⏳ Loading InsightFace Model...")
model = insightface.app.FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
model.prepare(ctx_id=0, det_size=(640, 640))

# Load Dataset (.npy files)
dataset_folder = "dataset"
known_faces = {}
if os.path.exists(dataset_folder):
    for file in os.listdir(dataset_folder):
        if file.endswith(".npy"):
            name = os.path.splitext(file)[0]
            path = os.path.join(dataset_folder, file)
            known_faces[name] = np.load(path)
            print(f"   Loaded: {name}")
else:
    print(f"❌ Error: '{dataset_folder}' folder not found.")
    exit()

# === 5. USER INPUT TARGET ===
print("\n-----------------------------")
target_user = input("🎯 Who should I follow? (Enter Name): ").strip()
print(f"🚀 Connecting to Android Camera at {ANDROID_IP}...")
print("-----------------------------\n")

# === 6. MAIN LOOP ===
# Use Android IP Camera URL instead of '0'
cap = cv2.VideoCapture(ANDROID_IP)

if not cap.isOpened():
    print("❌ Error: Could not connect to Android camera. Check IP and try again.")
    exit()

# Set resolution (Note: Some IP cams ignore this and use app settings)
cap.set(3, FRAME_WIDTH)
cap.set(4, FRAME_HEIGHT)

last_cmd = 'S'
last_spoken_time = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Frame not received. Exiting...")
        break

    # Resize frame to match processing size if needed
    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

    faces = model.get(frame)
    
    target_found = False
    cmd = 'S'
    status = "SEARCHING"
    
    screen_center_x = FRAME_WIDTH // 2
    
    # Draw Center Zone
    cv2.line(frame, (screen_center_x - CENTER_ZONE, 0), (screen_center_x - CENTER_ZONE, FRAME_HEIGHT), (0, 255, 0), 2)
    cv2.line(frame, (screen_center_x + CENTER_ZONE, 0), (screen_center_x + CENTER_ZONE, FRAME_HEIGHT), (0, 255, 0), 2)

    for face in faces:
        box = face.bbox.astype(int)
        name = identify_face(face.embedding, known_faces) or "Unknown"
        
        # Calculate Face Dimensions
        x, y, x2, y2 = box
        w = x2 - x
        cx = x + (w // 2)
        
        color = (0, 0, 255) # Red (Unknown)
        
        if name.lower() == target_user.lower():
            target_found = True
            color = (0, 255, 0) # Green (Target)
            
            # === STANDARD LOGIC (NO MIRROR) ===
            # Face on LEFT of screen -> Turn LEFT
            if cx < (screen_center_x - CENTER_ZONE):
                cmd = 'L'
                status = "TURNING LEFT"
            
            # Face on RIGHT of screen -> Turn RIGHT
            elif cx > (screen_center_x + CENTER_ZONE):
                cmd = 'R'
                status = "TURNING RIGHT"
            
            else:
                # Forward Logic
                if w < STOP_WIDTH:
                    cmd = 'F'
                    status = "FORWARD"
                else:
                    cmd = 'S'
                    status = "TARGET REACHED"
            
            if time.time() - last_spoken_time > 10:
                last_spoken_time = time.time()

        cv2.rectangle(frame, (x, y), (x2, y2), color, 2)
        cv2.putText(frame, f"{name} ({int(w)})", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    if not target_found:
        cmd = 'S'
        status = "SCANNING..."

    # Send Command
    if cmd != last_cmd:
        send_cmd(cmd)
        print(f"Sending Command: {cmd}")
        last_cmd = cmd

    cv2.putText(frame, f"TARGET: {target_user} | CMD: {cmd}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    cv2.putText(frame, f"STATUS: {status}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    cv2.imshow("Smart Robot Follower", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('h'):
        speak(f"Hello {target_user}")

send_cmd('S')
cap.release()
cv2.destroyAllWindows()
if arduino: arduino.close()