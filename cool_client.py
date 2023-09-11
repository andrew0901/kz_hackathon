import asyncio
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.signaling import TcpSocketSignaling
from av.video.frame import *
from PIL import Image
import cv2 as cv
from multiprocessing import Process, Queue
import os

event = asyncio.Event()
event.set()

async def consume_track(track:MediaStreamTrack):
    for i in range(50):
        frame:VideoFrame = await track.recv()
        #arr = frame.to_ndarray()
        #print(arr)
        img = frame.to_image()
        if i <10:
            img.save("recordedimg/img0"+str(i)+".jpg")
        else:
            img.save("recordedimg/img"+str(i)+".jpg")

        # if i == 0:
        #     with open("temp.png","wb") as f:
        #         f.write(frame.to_bytes())

        # event.set()


def compute_coordinate(files, queue):
    origin = cv.imread('./recordedimg/origin.jpg', 0)
    corner = cv.imread('./recordedimg/corner.jpg', 0)
    ball = cv.imread('./recordedimg/ball.jpg', 0)
    w, h = ball.shape[::-1]
    directory = "./recordedimg"

    for file in files:
        if file.lower().endswith('.jpg') and file.lower().startswith('img'):
            f = os.path.join(directory, file)
            img = cv.imread(f, 0)

            cv.imshow('Window', img)
            key = cv.waitKey(100) 
            if key == 27: #if ESC is pressed, exit loop
                cv.destroyAllWindows()
                break

            method = 3
            res = cv.matchTemplate(img,ball,method)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
            ball_x, ball_y = max_loc[0] + w, max_loc[1] + h
            
            res = cv.matchTemplate(img,origin,method)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
            origin_x, origin_y = max_loc[0] + w, max_loc[1] + h

            res = cv.matchTemplate(img,corner,method)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
            corner_x, corner_y = max_loc[0] + w, max_loc[1] + h
            
            x_coordinate = (ball_x-origin_x)/(corner_x-origin_x)*6-1
            y_coordinate = (origin_y-ball_y)/(origin_y-corner_y)*5
            coordinate = (round(x_coordinate,2), round(y_coordinate,2))
            queue.put(coordinate)

    



async def run():
    global event
    signaling = TcpSocketSignaling("127.0.0.1", 18889)
    pc = RTCPeerConnection()
    pc.on('track', lambda track:asyncio.create_task(consume_track(track)))
    await signaling.connect()
    print('connected')

    

    offer = await signaling.receive()
    await pc.setRemoteDescription(offer)
    print('offer received')

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    await signaling.send(answer)
    print('answer sent')
    
    await asyncio.sleep(3)

    queue = Queue()
    directory = "./recordedimg"
    files = sorted(os.listdir(directory))
    process_a = Process(target = compute_coordinate, args = (files, queue))
    process_a.start()
    process_a.join()
    while not queue.empty():
        print(queue.get())
    


    await pc.close()

if __name__ == "__main__":
    asyncio.run(run())