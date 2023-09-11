import asyncio
import fractions
import cv2
import numpy as np
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from av.video.frame import VideoFrame
from aiortc.contrib.signaling import TcpSocketSignaling
from ball import Ball

class VideoImageTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self):
        super().__init__()
        self.counter = 0



    async def recv(self):
        self.counter += 1
        img = np.zeros((500, 500, 3), dtype=np.uint8)
        img = cv2.putText(img, f'Frame {self.counter}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        frame = VideoFrame.from_ndarray(img, format='bgr24')
        frame.pts = self.counter
        frame.time_base = fractions.Fraction(1, 30)
        return frame

class FramesTransportTrack(VideoStreamTrack):

    kind = "video"
    def __init__(self):
        super().__init__() 
        self.counter = 0
        self.ball = Ball()
        #self.frames = []
        print('generating images')
        self.frames = self.ball.generate_frames()
        print('image generated')

    async def recv(self):
        #pts, time_base = await self.next_timestamp()
        pts, time_base = await self.next_timestamp()
        frame = self.frames[self.counter % 50]
        frame.pts = pts
        frame.time_base = time_base
        #frame.pts = pts
        #frame.time_base = time_base
        self.counter += 1
        return frame

pcs = set()
async def handle_connection(pc:RTCPeerConnection):
    pass


    # @pc.on("track")
    # def on_track(track):
    #     print("======= received track: ", track)
    #     if track.kind == "video":
    #         t = FaceSwapper(track)
    #         pc.addTrack(t)
async def run():
    signaling = TcpSocketSignaling("127.0.0.1", 18889)
    pc = RTCPeerConnection()
    pc_id = f"Server({pc})"
    await signaling.connect()

    pc.addTrack(FramesTransportTrack())
    #pc.addTrack(VideoImageTrack())

    print('wait for offer')
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    await signaling.send(pc.localDescription)
    print('offer sent')
    while True:
        answer = await signaling.receive()
        if answer is None:
            break
        await pc.setRemoteDescription(answer)
    await pc.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    # loop.create_task(run())
    # loop.run_forever()