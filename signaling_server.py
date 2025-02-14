import asyncio
import websockets
import json
import cv2
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from aiortc.contrib.media import MediaStreamTrack

# Create a MediaStreamTrack to capture video from the camera
class VideoStreamTrack(MediaStreamTrack):
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)  # Capture from the first camera (Raspberry Pi camera)

    async def recv(self):
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Failed to capture frame")
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame_rgb

# Function to handle WebRTC signaling
async def handle_webrtc_connection(websocket, path):
    peer_connection = RTCPeerConnection()

    # Add the video track to the peer connection
    video_track = VideoStreamTrack()
    peer_connection.addTrack(video_track)

    @peer_connection.on("icecandidate")
    async def on_icecandidate(candidate):
        if candidate:
            await websocket.send(json.dumps({"iceCandidate": candidate.to_dict()}))

    try:
        while True:
            message = await websocket.recv()
            data = json.loads(message)

            # Handle the offer from the laptop
            if "offer" in data:
                offer = RTCSessionDescription(sdp=data["offer"]["sdp"], type=data["offer"]["type"])
                await peer_connection.setRemoteDescription(offer)
                answer = await peer_connection.createAnswer()
                await peer_connection.setLocalDescription(answer)
                await websocket.send(json.dumps({"answer": peer_connection.localDescription.to_dict()}))

            # Handle ICE candidates
            if "iceCandidate" in data:
                candidate = RTCIceCandidate(
                    sdpMid=data["iceCandidate"]["sdpMid"],
                    sdpMLineIndex=data["iceCandidate"]["sdpMLineIndex"],
                    candidate=data["iceCandidate"]["candidate"]
                )
                await peer_connection.addIceCandidate(candidate)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the connection
        await peer_connection.close()

# WebSocket server to receive WebRTC signaling
async def start_signaling_server():
    async with websockets.serve(handle_webrtc_connection, "0.0.0.0", 8765):
        print("WebSocket server started at ws://0.0.0.0:8765")
        await asyncio.Future()

# Run WebSocket server
asyncio.run(start_signaling_server())
