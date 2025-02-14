import cv2
import numpy as np
import subprocess
import io

async def display_stream_on_projector(track):
    video_stream = track.recv()
    
    while True:
        frame = await video_stream.recv()
        frame_data = frame.to_ndarray(format="bgr24")
        
        _, buffer = cv2.imencode('.jpg', frame_data)
        byte_array = buffer.tobytes()

        gst_command = [
            "gst-launch-1.0", "fdsrc", "!", "jpegdec", "!", "videoconvert", "!", "autovideosink"
        ]
        
        process = subprocess.Popen(gst_command, stdin=subprocess.PIPE)
        process.stdin.write(byte_array)
        process.stdin.close()
        process.wait()
