import cv2
import time
import base64
import wave
import librosa
import os
import threading

import soundfile as sf
import numpy as np

lock = threading.Lock()

from streamlit_webrtc_display_capture import (
    WebRtcMode,
    RTCConfiguration,
    webrtc_streamer,
    create_mix_track
)

def window_capture(img_container, fps, record_seconds):
    processed_images = []
    base64Frames = []
    for i in range(int(record_seconds * fps)):
        tic = time.perf_counter()

        with lock:
            img = cv2.cvtColor(img_container["img"], cv2.COLOR_BGR2RGB)
        if img is None:
            continue
        processed_images.append(img)

        # convert img to numpy array to work with OpenCV
        frame = np.array(img)
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

        # Add delay to ensure frames are captured at the desired fps
        toc = time.perf_counter()
        while (toc - tic) < 1/fps:
            toc = time.perf_counter()
    
    return processed_images, base64Frames

def autoplay_audio(file_path: str, audio_container):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        audio_container.markdown(
            md,
            unsafe_allow_html=True,
        )
        
        #Time delay until audio finishes playing
        x,_ = librosa.load(file_path, sr=16000)
        sf.write('tmp.wav', x, 16000)
        time.sleep(get_duration_wave('tmp.wav'))
        os.remove("tmp.wav")
        audio_container.empty()


def get_duration_wave(file_path):
   with wave.open(file_path, 'r') as audio_file:
      frame_rate = audio_file.getframerate()
      n_frames = audio_file.getnframes()
      duration = n_frames / float(frame_rate)
      return duration
   
def get_webrtc_streamer(video_frame_callback):
    # Streamlit RTC    
    try:
        # Custom ICE Server
        urls = os.environ["ICE_SERVER"]
        username = os.environ["USER"]
        credential = os.environ["PASS"]
        rtc_configuration = RTCConfiguration(
            {
            "iceServers": [{
                "urls": [urls],
                "username": username,
                "credential": credential,
            }]
        })
    except KeyError:
        # Fallback option if no ICE server is provided
        # May or may not work in some network environments
        rtc_configuration = RTCConfiguration(
            {
                "iceServers": [{
                    "urls": ["stun:stun.l.google.com:19302"],
                }]
            }   
        )   

    self_ctx = webrtc_streamer(
        key="self",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=rtc_configuration,
        media_stream_constraints={"video": True, "audio": True},
        video_frame_callback=video_frame_callback,
        sendback_audio=False,
    )
    return self_ctx