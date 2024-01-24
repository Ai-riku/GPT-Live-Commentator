import streamlit as st
from data import *
from streamlit_webrtc import (
    RTCConfiguration,
    webrtc_streamer,
)

import os
import av


def webcam_input():
    st.header("Webcam Live Feed")

    def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
        image = frame.to_ndarray(format="bgr24")
        return image

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
        
    ctx = webrtc_streamer(
        key="neural-style-transfer",
        video_frame_callback=video_frame_callback,
        rtc_configuration=rtc_configuration,
        media_stream_constraints={"video": True, "audio": False},
    )