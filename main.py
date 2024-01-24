import threading
import time
import streamlit as st

from openai_utils import *
from utils import *

lock = threading.Lock()
img_container = {"img": None}

def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    with lock:
        img_container["img"] = img
    return frame

# Streamlit UI
def main():
    st.set_page_config(
        page_title="AI Live Commentary", 
        page_icon=":loudspeaker:",
        initial_sidebar_state='collapsed'
    )

    st.header("AI Live Commentary :loudspeaker:")

    # Options with UI
    if "prompt" not in st.session_state:
        st.session_state["prompt"] = "Provide exciting commentary!"
    prompt_input = st.text_area("Prompt:", value=st.session_state["prompt"], placeholder="Enter prompt for commentary or to generate prompt", )
    prompt = prompt_input
    if st.button("Generate prompt") and prompt is not None:
        with st.spinner('Generating...'):
            st.session_state["prompt"] = prompt_to_text(prompt)

    with st.sidebar:
        voice = st.selectbox('Select voice:', ("alloy", "echo", "fable", "onyx", "nova", "shimmer"))
        commentary_delay = st.number_input("Delay between commentary:", value=0)
        record_seconds = st.number_input("Seconds per input video:", value=5)
        fps = st.number_input("Frames captured per second:", value=1)
        est_word_count = st.number_input("Estimated word count:", value=10)
    
    # webrtc_streamer
    self_ctx = get_webrtc_streamer(video_frame_callback)
    
    # Display
    text_container = st.empty()
    audio_container = st.empty()
    aiImageHeader = st.empty()
    vision_container = st.empty()
    while self_ctx.state.playing and prompt is not None:
        if img_container["img"] is None:
            continue
        with st.spinner('Processing...'):
            final_prompt = prompt + f"(The text is meant to be read out over only {record_seconds} seconds, so make sure the response is less than {est_word_count} words)"
            aiImageHeader.subheader("AI Processed Images")
            images, base64Frames = window_capture(img_container, fps, record_seconds)
            with vision_container:
                st.image(images, width=130)
            try:
                text = frames_to_story(base64Frames, final_prompt)
            except Exception as e:
                print(e)
                continue
            with text_container: 
                with st.chat_message("assistant"):
                    st.write(text)
            audio_filename = text_to_audio(text, voice)
            autoplay_audio(audio_filename, audio_container)
            time.sleep(commentary_delay)


if __name__ == '__main__':
    main()