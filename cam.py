import urllib.request
import cv2 
import numpy as np
import time

url = 'http://192.168.1.244/320x240.jpg'

prev_frame_time = 0
new_frame_time = 0

while True:
    imgResp=urllib.request.urlopen(url)
    imgNp=np.array (bytearray(imgResp.read()), dtype=np.uint8)
    img=cv2.imdecode(imgNp, -1)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(gray)

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2) 

    new_frame_time = time.time() 
    fps = 1/(new_frame_time-prev_frame_time) 
    prev_frame_time = new_frame_time 
    fps = str(int(fps)) 
    cv2.putText(img, fps, (7, 70), cv2.FONT_HERSHEY_SIMPLEX , 3, (100, 255, 0), 3, cv2.LINE_AA) 


    cv2.imshow('test', img)
    if ord('q')==cv2.waitKey(10):
        exit(0)
cv2.destroyAllWindows()