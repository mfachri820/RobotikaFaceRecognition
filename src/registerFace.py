import cv2
import numpy as np
import insightface

# === Initialize InsightFace model ===
model = insightface.app.FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
model.prepare(ctx_id=0, det_size=(640, 640))

# === Open webcam ===
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("❌ Could not open webcam.")
    exit()

print("✅ Webcam ready. Press 'SPACE' to capture your face, or 'Q' to quit.")

captured = False
while True:
    ret, frame = cap.read()
    if not ret:
        break

    faces = model.get(frame)
    for face in faces:
        box = face.bbox.astype(int)
        cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0,255,0), 2)
        cv2.putText(frame, "Face Detected", (box[0], box[1]-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    cv2.imshow("Register Face", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord(' '):  # Press SPACE to capture
        if len(faces) > 0:
            name = input("Enter name to save as: ").strip()
            np.save(f"dataset/{name}.npy", faces[0].embedding)
            print(f"✅ Saved embedding as {name}.npy")
            captured = True
        else:
            print("⚠️ No face detected, try again.")
    elif key == ord('q'):
        break

    # Optional: exit automatically after capture
    if captured:
        break

cap.release()
cv2.destroyAllWindows()
