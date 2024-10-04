import RPi.GPIO as GPIO
import time

# 左のモーター
IN1 = 17
IN2 = 27
ENA = 18

# 右のモーター
IN3 = 22
IN4 = 23
ENB = 13

# PWM設定
GPIO.setmode(GPIO.BCM) # GPIOの番号を指定するモード
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)

pwmA = GPIO.PWM(ENA, 100)
pwmB = GPIO.PWM(ENB, 100)
pwmA.start(0)
pwmB.start(0)

def motor_left_foward(speed):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwmA.ChangeDutyCycle(speed)

def motor_right_foward(speed):
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwmB.ChangeDutyCycle(speed)

def motor_left_backward(speed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    pwmA.ChangeDutyCycle(speed)

def motor_right_backward(speed):
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwmB.ChangeDutyCycle(speed) 

def motor_stop():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    pwmA.ChangeDutyCycle(0)  
    pwmB.ChangeDutyCycle(0)

def motor_run(dx, dy, speed=50):
    try:
        if dx > 0 and dy > 0:
            print("顔が右下")
            motor_left_foward(speed)
            # motor_right_backward(speed)
            
        elif dx > 0 and dy < 0:
            print("顔が右上")
            motor_left_foward(speed)
            # motor_right_backward(speed)

        elif dx < 0 and dy > 0:
            print("顔が左下")
            motor_left_backward(speed)
            # motor_right_foward(speed)

        elif dx < 0 and dy < 0:
            print("顔が左上")
            motor_left_backward(speed)
            # motor_right_foward(speed)

        else:
            print("追跡を終了する")
            motor_stop()
    
    except KeyboardInterrupt:
        pass
        
