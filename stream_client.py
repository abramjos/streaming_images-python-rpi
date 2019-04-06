import cv2
import io
import socket
import struct
import time
import numpy as np
import RPi.GPIO as gpio
import picamera


# create socket and bind host
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 8600))
connection = client_socket.makefile('wb')
fourcc = cv2.VideoWriter_fourcc(*'XVID')
gpio.setup(11, gpio.OUT)
gpio.setup(12, gpio.OUT)

try:

    with picamera.PiCamera() as camera:
        camera.resolution = (320, 240)
        camera.framerate = 10
        vid_fps=camera.framerate
        print("FPS == %d"%vid_fps)
        out = cv2.VideoWriter('output.avi', fourcc, 10.0, (320,240))
    
        counter=0
        time.sleep(2)                       # give 2 secs for camera to initilize
        start = time.time()
        stream = io.BytesIO()

        print("Started camera\n\n")
        end=struct.pack('<l', 11111111)
        end_str=end
        capture=struct.pack('<l', 10000001)
        cap_str=capture
                
        
        for foo in camera.capture_continuous(stream, 'jpeg', use_video_port = True):# send jpeg format video stream
            stream.seek(0)
            jpg=stream.read()
            frame=cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)
            stream.seek(0)

            key=cv2.waitKey(1)
            # print("pressed key= %c",key)
            timestamp=str(int(time.time()))
            #connection.write(np.array(buf).tostring())                    
            connection.flush()
            cv2.imshow("image",frame)
            out.write(frame)

            if key & 0xFF == ord('k'):

                connection.flush()
                print(timestamp)
                connection.write(cap_str)
                connection.write(timestamp)# np.array(buf).tostring())
                size=str(len(jpg))
                str_size=size.zfill(10)
                connection.write(str_size)
                connection.write(jpg)                    
                connection.flush()
                counter+=1

                continue

            elif key & 0xFF == ord('q'):
                connection.flush()
                connection.write(end_str)
                print("Connection Closed")
                break
            
            connection.flush()
            # connection.seek(0)
        
finally:
    connection.close()
    client_socket.close()
    out.release()
    cv2.destroyAllWindows()
