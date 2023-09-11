from aiortc.contrib.signaling import TcpSocketSignaling, object_to_string
from aiortc import MediaStreamTrack, RTCPeerConnection, VideoStreamTrack
from PIL import Image
import asyncio
import socket
import os
from ball import Ball

PORT = 5000
SERVER = socket.gethostbyname(socket.gethostname())

class FramesTransportTrack(VideoStreamTrack):

    kind = "video"
    
    def __init__(self):
        super().__init__() 
        self.counter = 0
        self.ball = Ball()
        self.frams = self.ball.generate_frames()

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        frame = self.frames[self.counter % 50]
        frame.pts = pts
        frame.time_base = time_base
        self.counter += 1
        return frame


async def run(signaling, pc):
    await signaling.connect()
    print('server connected')
    mst = FramesTransportTrack()
    pc.addTrack(mst)
    desc = await pc.createOffer() # RTCSessionDescription
    await pc.setLocalDescription(desc)
    await signaling.send(desc) 
    # create an aiortc offer and send
    print('offer sent')

    print(mst.recv())

    answer = await signaling.receive()
    await pc.setRemoteDescription(answer)
    print("answer received")
    await signaling.close()
#     # receive answer



signaling = TcpSocketSignaling(SERVER, PORT)
pc = RTCPeerConnection()

coro = run(signaling, pc)
asyncio.run(coro)