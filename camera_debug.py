import cv2
import time

print("=========================================")
print("        CAMERA DEBUGGER - Fachri         ")
print("=========================================\n")

# --- Step 1: Scan available camera indexes ---
print("🔍 Scanning camera indexes...")
working_cameras = []

for index in range(5):
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # DirectShow backend (Windows fix)
    time.sleep(0.3)

    if cap is not None and cap.isOpened():
        print(f"   ✔ Camera index {index} is AVAILABLE")
        working_cameras.append(index)
    else:
        print(f"   ✖ Camera index {index} is NOT available")

    if cap:
        cap.release()

if not working_cameras:
    print("\n❌ ERROR: No cameras detected at all!")
    exit()

print("\nAvailable cameras:", working_cameras)

# --- Step 2: Choose a camera to test ---
test_index = int(input("\n🎥 Enter camera index to test: "))

print(f"\n📷 Attempting to open camera index {test_index}...\n")

# Use DirectShow to avoid OpenCV highgui errors
cap = cv2.VideoCapture(test_index, cv2.CAP_DSHOW)

# --- Apply Logitech C525 Recommended Fixes ---
print("⚙ Applying camera settings...")

# Force MJPG first (Logitech fix)
fourcc_mjpg = cv2.VideoWriter_fourcc(*"MJPG")
cap.set(cv2.CAP_PROP_FOURCC, fourcc_mjpg)

# Force resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Force FPS
cap.set(cv2.CAP_PROP_FPS, 30)

# Try disabling auto exposure
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Manual
cap.set(cv2.CAP_PROP_EXPOSURE, -6)

# Disable autofocus if supported
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)

time.sleep(0.5)

# --- Step 3: Try reading frames ---
print("\n🎞 Testing camera feed...\n")

retry = 0
max_retry = 30
frame_ok = False

while retry < max_retry:
    ret, frame = cap.read()
    if ret and frame is not None:
        frame_ok = True
        break
    retry += 1
    print(f"   Waiting for frame... ({retry}/{max_retry})")
    time.sleep(0.1)

# If MJPG fails, try YUY2
if not frame_ok:
    print("\n⚠ MJPG failed. Trying YUY2...")
    cap.release()

    cap = cv2.VideoCapture(test_index, cv2.CAP_DSHOW)
    fourcc_yuy2 = cv2.VideoWriter_fourcc(*"YUY2")
    cap.set(cv2.CAP_PROP_FOURCC, fourcc_yuy2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    time.sleep(0.5)

    # Try reading again
    retry = 0
    while retry < max_retry:
        ret, frame = cap.read()
        if ret and frame is not None:
            frame_ok = True
            break
        retry += 1
        print(f"   Waiting for frame (YUY2)... ({retry}/{max_retry})")
        time.sleep(0.1)

if not frame_ok:
    print("\n❌ ERROR: Camera opened but no frames received!")
    print("   ➜ C525 Driver conflict or camera in use.")
    print("   ➜ Try:")
    print("     - Cabut / colok ulang webcam")
    print("     - Tutup Zoom/Discord/Chrome/Camera App")
    print("     - Coba port USB lain (hindari USB 3.0 biru)")
    print("     - Restart laptop")
    cap.release()
    exit()

print("✅ Camera is working! Opening preview window...\n")

# --- Step 4: Display camera window ---
while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠ Lost camera signal.")
        break

    cv2.imshow(f"Camera {test_index} - Press Q to exit", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("\n🔚 Camera test ended. Goodbye!")
