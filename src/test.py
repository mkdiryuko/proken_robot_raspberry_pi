import cv2
import time 
import openai
import os

# OpenCV face_recognition_model
model_url = "/home/proken/workspace/proken_robot/assets/haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(model_url)

video_url = "http://172.20.10.4:8080/video"
audio_url = "http://172.20.10.3:8080/audio.wav"

openai.api_key = os.getenv("OPENAI_API_KEY")

if face_cascade.empty():
    print("Error: Could not load Haar Cascade file.")

cap = cv2.VideoCapture(video_url)

ret, frame = cap.read()

# cap center                                                            
height, width = frame.shape[:2]
cap_center_x = width // 2
cap_center_y = height // 2

last_faces = []

last_detection_time = 0
detection_interval = 2

while True:
    ret, frame = cap.read()

    if not ret:
        print('not read camera')
        break

    current_time = time.time()

    if current_time - last_detection_time > detection_interval:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # face detection 
        last_faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        last_detection_time = current_time 

    if len(last_faces) > 0:
        for (x, y, w, h) in last_faces:
            # ROI内での座標をフレーム全体の座標に変換
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            center_x = x + w // 2
            center_y = y + h // 2
            cv2.circle(frame, (center_x, center_y), 2, (255, 0, 0), 2)
            cv2.line(frame, (center_x, center_y),(cap_center_x, cap_center_y),(255, 0, 0),2)

    cv2.imshow("Face Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()