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

load_dotenv()

SERIAL_PORT = 'COM16'
BAUD_RATE = 9600

FRAME_WIDTH = 640
FRAME_HEIGHT = 480
CENTER_ZONE = 100
STOP_WIDTH = 110

API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"
MODEL_ID = "eleven_flash_v2_5"

# ================================================
# 🔥 DEBUG: SERIAL CONNECTION CHECK
# ================================================
arduino = None
try:
    print(f"[DEBUG] Attempting Arduino connection on {SERIAL_PORT} ...")
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)

    arduino.reset_input_buffer()
    arduino.reset_output_buffer()

    print(f"✅ [DEBUG] Arduino connected on {SERIAL_PORT}")
except Exception as e:
    print(f"❌ [DEBUG] Arduino connection failed: {e}")
    print("[DEBUG] Listing available ports:")
    for p in serial.tools.list_ports.comports():
        print(f" - {p.device}")
    print("⚠ Running in VISION ONLY MODE")
    

# ================================================
# 🔥 DEBUG: SERIAL SEND FUNCTION
# ================================================
def send_cmd(command):
    if not arduino:
        print(f"[DEBUG] No Arduino. Command {command} skipped.")
        return
    
    msg = command + "\n"
    print(f"[DEBUG] Sending serial → {repr(msg)}")

    try:
        arduino.write(msg.encode())
    except Exception as e:
        print(f"❌ [DEBUG] Serial Send Error: {e}")


# ================================================
# FACE IDENTIFICATION
# ================================================
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def identify_face(embedding, database, threshold=0.35):
    best_match = None
    highest_score = threshold
    for name, emb in database.items():
        score = cosine_similarity(embedding, emb)
        print(f"[DEBUG] Comparing with {name}: score={score:.3f}")
        if score > highest_score:
            best_match = name
            highest_score = score
    return best_match


# ================================================
# 🔥 DEBUG: LOAD MODEL
# ================================================
print("[DEBUG] Loading InsightFace model...")
model = insightface.app.FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
model.prepare(ctx_id=0, det_size=(640, 640))
print("✅ [DEBUG] Model loaded.")


# ================================================
# 🔥 DEBUG: LOAD DATASET
# ================================================
dataset_folder = "dataset"
known_faces = {}

print("[DEBUG] Loading dataset...")
if os.path.exists(dataset_folder):
    for file in os.listdir(dataset_folder):
        if file.endswith(".npy"):
            name = os.path.splitext(file)[0]
            path = os.path.join(dataset_folder, file)
            known_faces[name] = np.load(path)
            print(f"   Loaded → {name}")
else:
    print(f"❌ Dataset folder '{dataset_folder}' not found.")
    exit()

# ================================================
# INPUT TARGET
# ================================================
print("\n-----------------------------")
target_user = input("🎯 Who should I follow? ").strip()
print(f"[DEBUG] Selected target = {target_user}")
print("-----------------------------\n")


# ================================================
# MAIN LOOP WITH DEBUG PRINTS
# ================================================
cap = cv2.VideoCapture(0)
cap.set(3, FRAME_WIDTH)
cap.set(4, FRAME_HEIGHT)

last_cmd = None

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ [DEBUG] Camera read failed.")
        break

    faces = model.get(frame)
    print(f"[DEBUG] Faces detected: {len(faces)}")

    target_found = False
    cmd = 'S'
    
    screen_center_x = FRAME_WIDTH // 2

    for face in faces:
        box = face.bbox.astype(int)
        name = identify_face(face.embedding, known_faces) or "Unknown"
        
        x, y, x2, y2 = box
        w = x2 - x
        cx = x + (w // 2)

        print(f"[DEBUG] Face '{name}' at X={cx}, width={w}")

        if name.lower() == target_user.lower():
            target_found = True
            print("[DEBUG] TARGET FOUND")

            if cx < (screen_center_x - CENTER_ZONE):
                cmd = 'L'
                print("[DEBUG] Decision → TURN LEFT")

            elif cx > (screen_center_x + CENTER_ZONE):
                cmd = 'R'
                print("[DEBUG] Decision → TURN RIGHT")

            else:
                if w < STOP_WIDTH:
                    cmd = 'F'
                    print("[DEBUG] Decision → FORWARD")
                else:
                    cmd = 'S'
                    print("[DEBUG] Decision → STOP (close enough)")

        else:
            print("[DEBUG] Non-target face ignored.")

    if not target_found:
        print("[DEBUG] No target found → SCANNING")
        cmd = 'S'

    # SERIAL COMMAND
    if cmd != last_cmd:
        print(f"[DEBUG] Sending command: {cmd}")
        send_cmd(cmd)
        last_cmd = cmd
    else:
        print(f"[DEBUG] Command unchanged ({cmd}) → not sent again")

    # Show window
    cv2.imshow("DEBUG VIEW", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


send_cmd("S")
cap.release()
cv2.destroyAllWindows()
if arduino:
    arduino.close()
