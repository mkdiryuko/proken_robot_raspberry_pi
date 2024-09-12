import serial 
import time

ser = serial.Serial('/dev/ttyACM0', 9600)

for i in range(10):
    ser.write(1)
    print("LED ON")
    time.sleep(0.5)
    ser.write(0)
    print("LED OFF")
    time.sleep(0.5)

ser.close()
print("bbb")