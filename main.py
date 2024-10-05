from openai import OpenAI
import cv2
import numpy as np
import os
import RPi.GPIO as GPIO
import sys
import time

from src import conversation, audio_record
from src.motor_control import forward, backward, rotate, motor_stop

time.sleep(2)

current_dir = os.path.dirname(os.path.abspath(__file__))
model_url = os.path.join(current_dir, "assets/haarcascade_frontalface_default.xml") # OpenCVが提供する顔検出モデル
face_cascade = cv2.CascadeClassifier(model_url)

if face_cascade.empty():
    print("Error: Could not load Haar Cascade file.")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 30)

ret, frame = cap.read()
# frame = cv2.resize(frame)

# 追跡対象の設定
tracking = False

# 接近完了フラグ
approach = 0

pre_x = []

# カメラ画面の中心                                                          
height, width = frame.shape[:2]
cap_center_x = width // 2
cap_center_y = height // 2

# 見つけた顔を格納するリスト
last_faces = []

# 処理が重いので顔検出は2秒に一回
last_detection_time = 0
detection_interval = 2

# トラッカーモデルの作成
tracker = cv2.TrackerKCF_create()

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
    # frame = cv2.resize(frame, (640, 480))

    if not ret or frame is None:
        print('not read camera')
        continue

    current_time = time.time()

    # 追跡対象がなければ、カメラ画面の中心から最も遠い顔を選択する
    if not tracking:
        if current_time - last_detection_time > detection_interval:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # 顔検出
            last_faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
            last_detection_time = current_time 

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
            tracking = True
            (x, y, w, h) = selected_face
            # トラッカーを設定
            tracker.init(frame, (x, y, w, h))
            print("追跡対象を設定しました")
    
    # 追跡開始
    else:
        success, bbox = tracker.update(frame)
        if success:
            x, y, w, h = [int(v) for v in bbox]
            face_center = detect_face_center(x, w, y, h)
            print(x)
            dx = face_center[0] - cap_center_x
            dy = face_center[1] - cap_center_y
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # カメラの中心に顔が来たら終了
            if (abs(dx) > 30):
                print("ターゲットを中心に設定します")
                # rotate(dx, dy)
            # elif (h < 100):
            #     print("ターゲットに近づきます")
            #     forward()
            # elif (h > 150):
            #     print("ターゲットから遠ざかります")
            #     backward()
            else: #　タイヤのモーター制御
                print("追跡を終了します。")
                motor_stop()
                tracking = False
                approach += 1
                tracker = cv2.TrackerKCF_create()
                print("トラッカーの再設定")

            # トラッカーのフリーズ対策
            pre_x.append(x)
            if len(pre_x) == 20:
                ave_x = sum(pre_x) / 20
                if abs(ave_x - x) <= 10:
                    print("フリーズの可能性あり!!")
                    tracking = False
                    tracker = cv2.TrackerKCF_create()
                pre_x = []
            print(pre_x)

            # 会話の処理
            if approach == 50:
              # 会話可能なことを伝える
              conversation_ok = conversation.jtalk_mei("こんにちは、話しかけてください")
              # ロボットに話しかけた声を録音する
              talkfile_path = audio_record.audio_record()

              # 録音した音声をテキスト化
              talk_text = conversation.audio_convert_text(talkfile_path)
              # 応答を作成する間、考え中...とつぶやく

              # 応答の作成
              res_text = conversation.create_conversation_text(talk_text)
              # 応答を音声に変換する
              conversation.jtalk_mei(f"こんにちは,{res_text}")
              approach = 0
        
        else:
            print("対象を見失いました")
            tracking = False
            tracker = cv2.TrackerKCF_create()

    cv2.imshow("Face Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        GPIO.cleanup()
        break

cap.release()
cv2.destroyAllWindows()