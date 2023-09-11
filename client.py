from aiortc.contrib.signaling import TcpSocketSignaling,BYE
from aiortc.contrib.media import MediaRecorder
from aiortc import MediaStreamTrack,RTCPeerConnection,RTCIceCandidate, RTCSessionDescription
import asyncio
import socket
import cv2
from ball import Ball

PORT = 5000
SERVER = socket.gethostbyname(socket.gethostname())

class FramesTransportTrack(MediaStreamTrack):

    kind = "video"
    def __init__(self):
        super().__init__() 
        self.counter = 0
        self.ball = Ball()
        #self.frames = []
        self.frames = self.ball.generate_frames()

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        frame = self.frames[self.counter % 50]
        frame.pts = pts
        frame.time_base = time_base
        self.counter += 1
        return frame

async def run(signaling, pc, recorder):
    
    @pc.on("track")
    def on_track(track):
        print("Receiving %s" % track.kind)
        print(track)
        recorder.addTrack(track)
        a = track.recv()
        print(a)
    
    '''
    while True:
        obj = await signaling.receive()

        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)
            await recorder.start()

            if obj.type == "offer":
                # send answer
                t = pc.addTrack(FramesTransportTrack())
                await pc.setLocalDescription(await pc.createAnswer())
                await signaling.send(pc.localDescription)
        elif isinstance(obj, RTCIceCandidate):
            await pc.addIceCandidate(obj)
        elif obj is BYE:
            print("Exiting")
            break
    '''

    
    
    # receive the offer from server
    await signaling.connect()
    print('connected')

    # while True:
    desc = await signaling.receive()
        # if isinstance(desc, RTCSessionDescription):

    await pc.setRemoteDescription(desc)
    print('offer received: ')
    await recorder.start()
    print("recorder started")

    #print(desc)

    answer = await pc.createAnswer()
    await signaling.send(answer) 
    print("answer sent")
    

    #await recorder.start()

# create an aiortc answer and send
# await pc.setLocalDescription(await pc.createAnswer())
# await signaling.send(pc.localDescription)
    await signaling.close()



signaling = TcpSocketSignaling(SERVER, PORT)
pc = RTCPeerConnection()
recorder = MediaRecorder("/recordedimg/img-%3d.jpg")

coro = run(signaling, pc, recorder)
asyncio.run(coro)





# RTCRtpReceiver
# create data channel