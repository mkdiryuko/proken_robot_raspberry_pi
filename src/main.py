import cv2
import numpy as np
import time 

# OpenCV face_recognition_model
model_url = "/home/proken/workspace/proken_robot/assets/haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(model_url)

if face_cascade.empty():
    print("Error: Could not load Haar Cascade file.")

url = "http://172.20.10.3:8080/video"

cap = cv2.VideoCapture(url)

ret, frame = cap.read()

# cap center                                                            
height, width = frame.shape[:2]
cap_center_x = width // 2
cap_center_y = height // 2

# face
last_faces = []

last_detection_time = 0
detection_interval = 2

def detect_face_center(x,width,y,height):
    center_x = x + width // 2
    center_y = y + height // 2
    return center_x, center_y

def face_distance(face_center_x, face_center_y, center_x, center_y):
    face_distance_x = center_x - face_center_x
    face_distance_y = center_y - face_center_y
    return face_distance_x, face_distance_y

while True:
    ret, frame = cap.read()

    if not ret:
        print('not read camera')
        break

    current_time = time.time()

    if current_time - last_detection_time > detection_interval:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # face detection 
        last_faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
        last_detection_time = current_time 

    max_distance = 0
    selected_face = None

    if len(last_faces) > 0:
        for (x, y, w, h) in last_faces:
            # ROI内での座標をフレーム全体の座標に変換
            face_center_x, face_center_y = detect_face_center(x, w, y, h) 
            face_distance_x, face_distance_y = face_distance(face_center_x, face_center_y, cap_center_x, cap_center_y)
            distance = np.sqrt((face_center_x - cap_center_x) ** 2 + (face_center_y - cap_center_y) ** 2)

            if distance > max_distance:
                max_distance = distance
                selected_face = (x, y, w, h)
            
        if selected_face is not None:
            (x, y, w, h) = selected_face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            # cv2.circle(frame, (face_center_x, face_center_y), 2, (255, 0, 0), 2)
            # cv2.line(frame, (face_center_x, face_center_y),(cap_center_x, cap_center_y),(255, 0, 0),2)
            cv2.putText(frame, f"({str(face_distance_x)}, {str(face_distance_y)})", (50,250), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.imshow("Face Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()