import asyncio
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.signaling import TcpSocketSignaling
from av.video.frame import *
from PIL import Image
event = asyncio.Event()
event.set()

async def consume_track(track:MediaStreamTrack):
    for i in range(100):
        frame:VideoFrame = await track.recv()
        #arr = frame.to_ndarray()
        #print(arr)
        img = frame.to_image()
        img.save("recordedimg/img"+str(i)+".jpg")
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
    print('connected')


    offer = await signaling.receive()
    await pc.setRemoteDescription(offer)
    print('offer received')

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    await signaling.send(answer)
    print('answer sent')
    await asyncio.sleep(10)
    await pc.close()

if __name__ == "__main__":
    asyncio.run(run())