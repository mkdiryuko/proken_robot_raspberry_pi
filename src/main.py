import cv2
import numpy as np
import time 
import serial

# シリアル通信の設定
ser = serial.Serial('/dev/ttyACM0', 9600)
time.sleep(2)

# OpenCVが提供する顔検出モデル
model_url = "/home/proken/workspace/proken_robot/assets/haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(model_url)

if face_cascade.empty():
    print("Error: Could not load Haar Cascade file.")

url = "http://172.20.10.3:8080/video"

cap = cv2.VideoCapture(url)

ret, frame = cap.read()

# 追跡対象の設定
target_face = None
tracking = False

# カメラ画面の中心                                                          
height, width = frame.shape[:2]
cap_center_x = width // 2
cap_center_y = height // 2

# 見つけた顔を格納するリスト
last_faces = []

# 処理が重いので顔検出は2秒に一回
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

        # 顔検出
        last_faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
        last_detection_time = current_time 

    # 追跡対象がなければ、カメラ画面の中心から最も遠い顔を選択する
    if not tracking:
        max_distance = 0
        selected_face = None

        if len(last_faces) > 0:
            for (x, y, w, h) in last_faces:
                # カメラ画面の中心と顔の中心との距離を計算
                face_center_x, face_center_y = detect_face_center(x, w, y, h) 
                face_distance_x, face_distance_y = face_distance(face_center_x, face_center_y, cap_center_x, cap_center_y)
                distance = np.sqrt((face_center_x - cap_center_x) ** 2 + (face_center_y - cap_center_y) ** 2)

                if distance > max_distance:
                    max_distance = distance
                    selected_face = (x, y, w, h)
            
        if selected_face is not None:
            target_face = selected_face
            tracking = True
            (x, y, w, h) = selected_face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(frame, f"({str(face_distance_x)}, {str(face_distance_y)})", (50,250), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            print("追跡対象を設定しました")
    
    # 追跡対象が設定されれば
    if tracking:
        x, y, w, h = target_face
        face_center = detect_face_center(x, w, y, h)
        dx = face_center[0] - cap_center_x
        dy = face_center[1] - cap_center_y

        # arduinoにdx, dyの情報を送る
        data = f"{dx}, {dy}\n"
        ser.write(data.encode('utf-8'))
        print(f"Sending dx: {dx}, dy: {dy}")   

        # カメラの中心に顔が来たら終了
        if (abs(dx) < 10 and abs(dy) < 10):
            print("追跡を終了します。")
            tracking = False
    
    # タイヤの動作を待つ
    time.sleep(1)


    cv2.imshow("Face Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()