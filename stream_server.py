
import numpy as np
import cv2
import serial
import socket


class CollectTrainingData(object):
    
    def __init__(self,public_ip,port):
        ip_address=socket.gethostbyaddr(public_ip)[0]
        self.server_video = socket.socket()
        self.server_video.bind((ip_address, port))
        self.server_video.listen(0)

        # accept a two connection
        self.video, self.client_address_video = self.server_video.accept()
    	print "Connection from: ", self.client_address_video
        self.video = self.video.makefile('rb')
        self.send_inst = True

        self.collect_image()

    def collect_image(self):

        total_frame = 0

        # collect images for training
        print 'Start collecting images...'
        e1 = cv2.getTickCount()

        # stream video frames one by one
        try:
            stream_bytes = ''
            frame = 1
            while self.send_inst:

                stream_bytes += self.video.read(1024)                
                
                
                if stream_bytes.find('\x81\x96\x98\x00')!=-1:
                    
                    cap_str=stream_bytes.find('\x81\x96\x98\x00')+4

                    timestamp=int(stream_bytes[cap_str:cap_str+10])
                    print(timestamp)
                    # import ipdb;ipdb.set_trace()
                                        
                    stream_bytes=stream_bytes[cap_str+10:]
                    stream_size=stream_bytes[:10]
                    print(stream_size)

                    stream_bytes += self.video.read(int(stream_size))
                    first = stream_bytes.find('\xff\xd8')
                    last = stream_bytes.find('\xff\xd9')
                    print(first,last)

                    if first != -1 and last != -1:

                        jpg = stream_bytes[first:last + 2]

                        print("\tImage @ -%d"%timestamp)
                        image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)
                        cv2.imwrite('im/image-%d.jpg'%timestamp, image)
                        #print(image)

                        total_frame += 1
                    else:
                        continue

    

                elif stream_bytes.find('\xc7\x8a\xa9\x00')!=-1:
                   self.send_inst=False
                   continue

                else:
                    stream_bytes=''
                    continue


            e2 = cv2.getTickCount()
            # calculate streaming duration
            time0 = (e2 - e1) / cv2.getTickFrequency()
            print 'Streaming duration:', time0

            print 'Total frame:', total_frame

        finally:
            self.video.close()
            self.server_video.close()

if __name__ == '__main__':
    CollectTrainingData('127.0.0.1', 8600)


