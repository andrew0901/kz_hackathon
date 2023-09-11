from aiortc.contrib.signaling import TcpSocketSignaling, BYE
from aiortc.contrib.media import MediaRecorder
from aiortc import RTCPeerConnection, RTCSessionDescription
import asyncio
import socket
import cv2
from server import FramesTransportTrack

PORT = 5000
SERVER = socket.gethostbyname(socket.gethostname())

async def run(signaling, pc, recorder):
    
    @pc.on("track")
    def on_track(track):
        print("Receiving %s" % track.kind)
        print(track)
        recorder.addTrack(track)

    # receive the offer from server
    await signaling.connect()
    print('connected')

    
    while True:
        obj = await signaling.receive()

        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)
            await recorder.start()

            if obj.type == "offer":
                print("offer received")
                # send answer
                pc.addTrack(FramesTransportTrack())
                print("track added")
                await pc.setLocalDescription(await pc.createAnswer())
                await signaling.send(pc.localDescription)
                print("answer sent")
        elif obj is BYE:
            print("Exiting")
            break

    '''
    # while True:
    desc = await signaling.receive()
        # if isinstance(desc, RTCSessionDescription):
    print("here")

    await pc.setRemoteDescription(desc)
    print('offer received: ')
    #print(desc)

    #pc.addTrack(FramesTransportTrack())
    #print("track added")

    answer = await pc.createAnswer()
    await signaling.send(answer) 
    print("answer sent")
    '''
    
    #await recorder.start()


# create an aiortc answer and send
# await pc.setLocalDescription(await pc.createAnswer())
# await signaling.send(pc.localDescription)
    await signaling.close()



signaling = TcpSocketSignaling(SERVER, PORT)
pc = RTCPeerConnection()
recorder = MediaRecorder("/recordedimg/img-%3d.png")

coro = run(signaling, pc, recorder)
asyncio.run(coro)





# RTCRtpReceiver
# create data channel