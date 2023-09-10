from aiortc.contrib.signaling import TcpSocketSignaling, object_to_string
from aiortc import MediaStreamTrack, RTCPeerConnection, VideoStreamTrack
from PIL import Image
import asyncio
import socket
import os

PORT = 5000
SERVER = socket.gethostbyname(socket.gethostname())

class FramesTransportTrack(MediaStreamTrack):

    kind = "video"
    def __init__(self):
        super().__init__() 
        self.frames = []
        directory = "./img"
        for file in os.listdir(directory):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                f = os.path.join(directory, file)
                img = Image.open(f)
                self.frames.append(img)
                
        

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        frame = self.frames[pts]
        frame.pts = pts
        frame.time_base = time_base
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
    await signaling.close()
#     # receive answer



signaling = TcpSocketSignaling(SERVER, PORT)
pc = RTCPeerConnection()

coro = run(signaling, pc)
asyncio.run(coro)