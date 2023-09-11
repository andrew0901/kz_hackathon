import asyncio
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.signaling import TcpSocketSignaling
from av.video.frame import *
event = asyncio.Event()
event.set()

async def consume_track(track:MediaStreamTrack):
    for i in range(1000):
        frame:VideoFrame = await track.recv()
        arr = frame.to_ndarray()
        print(arr)
        # if i == 0:
        #     with open("temp.png","wb") as f:
        #         f.write(frame.to_bytes())

        # event.set()
async def run():
    global event
    signaling = TcpSocketSignaling("127.0.0.1", 18889)
    pc = RTCPeerConnection()
    pc.on('track', lambda track:asyncio.create_task(consume_track(track)))
    await signaling.connect()

    offer = await signaling.receive()
    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    await signaling.send(answer)
    await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(run())