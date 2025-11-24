import cv2
import numpy as np
import insightface
import os
import time
import serial
from dotenv import load_dotenv

# === CONFIG ===
SERIAL_PORT = 'COM17'
BAUD_RATE = 9600

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

CENTER_ZONE = 160
STOP_WIDTH = 105

SMOOTHING = 0.30
STABLE_FRAMES = 2
PULSE = 0.15

load_dotenv()

# === ARDUINO ===
arduino = None
try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print("Arduino OK")
except:
    print("Arduino OFF")

def pulse(cmd):
    if arduino:
        arduino.write(cmd.encode())
        time.sleep(PULSE)
        arduino.write(b'S')
    print("PULSE:", cmd)

def send_cmd(cmd):
    if arduino:
        arduino.write(cmd.encode())
    print("CMD:", cmd)


# === LOAD MODEL (FASTER VERSION) ===
print("Loading InsightFace (FAST MODE)...")
model = insightface.app.FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)
model.prepare(ctx_id=0, det_size=(320, 320))   # <<< FASTER


# === LOAD DATASET ===
known = {}
for f in os.listdir("dataset"):
    if f.endswith(".npy"):
        known[f[:-4]] = np.load("dataset/" + f)
        print("Loaded:", f[:-4])

def cos_sim(a, b):
    return np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))

def identify(emb):
    best, score = None, 0.45
    for name, db in known.items():
        s = cos_sim(emb, db)
        if s > score:
            best = name
            score = s
    return best


target_user = input("Follow who? ").strip().lower()


# === CAMERA ===

print("Opening camera safely...")

# Use DirectShow (Windows)
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

# Apply same settings as debugger
fourcc_mjpg = cv2.VideoWriter_fourcc(*"MJPG")
cap.set(cv2.CAP_PROP_FOURCC, fourcc_mjpg)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
cap.set(cv2.CAP_PROP_FPS, 30)

time.sleep(0.5)  # warmup (VERY IMPORTANT)

# Check if camera ready
ret, frame = cap.read()
if not ret:
    print("⚠ Camera not giving frames, retrying...")
    time.sleep(1)

    cap.release()
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FOURCC, fourcc_mjpg)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 30)
    time.sleep(0.5)

    ret, frame = cap.read()
    if not ret:
        raise Exception("❌ Camera 1 failed even after retry!")

print("Camera READY ✓\n")


# === STATE ===
smoothed_cx = None
stable = 0
last_cmd = "S"

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)

    faces = model.get(frame)

    screen_center = FRAME_WIDTH // 2

    # Draw lines
    cv2.line(frame,(screen_center-CENTER_ZONE,0),(screen_center-CENTER_ZONE,FRAME_HEIGHT),(0,255,0),2)
    cv2.line(frame,(screen_center+CENTER_ZONE,0),(screen_center+CENTER_ZONE,FRAME_HEIGHT),(0,255,0),2)

    cmd = last_cmd
    status = "Searching"

    if faces:
        face = max(faces, key=lambda f: f.bbox[2]-f.bbox[0])
        x1,y1,x2,y2 = face.bbox.astype(int)
        w = x2 - x1
        cx = x1 + w//2

        cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)

        # Only embed if big enough (boost FPS)
        if w > 40:
            name = identify(face.embedding)
        else:
            name = None

        if name and name.lower() == target_user:

            # Smooth movement
            if smoothed_cx is None:
                smoothed_cx = cx
            else:
                smoothed_cx = int(smoothed_cx*(1-SMOOTHING) + cx*SMOOTHING)

            # LEFT
            if smoothed_cx < screen_center - CENTER_ZONE:
                stable += 1
                if stable >= STABLE_FRAMES:
                    pulse("L")
                    cmd = "L"
                    status = "LEFT"

            # RIGHT
            elif smoothed_cx > screen_center + CENTER_ZONE:
                stable += 1
                if stable >= STABLE_FRAMES:
                    pulse("R")
                    cmd = "R"
                    status = "RIGHT"

            else:
                stable = 0
                if w < STOP_WIDTH:
                    if last_cmd != "F":
                        send_cmd("F")
                    cmd = "F"
                    status = "FORWARD"
                else:
                    if last_cmd != "S":
                        send_cmd("S")
                    cmd = "S"
                    status = "STOP"

        else:
            smoothed_cx = None
            stable = 0

    else:
        smoothed_cx = None
        stable = 0
        if last_cmd != "S":
            send_cmd("S")
        cmd = "S"

    last_cmd = cmd

    cv2.putText(frame,f"CMD:{cmd}",(10,35),cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,0),2)
    cv2.putText(frame,status,(10,65),cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,0),2)

    cv2.imshow("Follower HighFPS", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

send_cmd("S")
cap.release()
cv2.destroyAllWindows()
