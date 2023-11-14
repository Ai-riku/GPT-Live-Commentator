import cv2
import pyautogui
import pywinauto
import time
import base64
import os
import requests
import tempfile
import string
import random
import wave
import librosa

import pygetwindow as gw
import streamlit as st
import numpy as np
import soundfile as sf

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def window_capture(window_name, fps, record_seconds, display_container):
    # seach and activate window
    w = gw.getWindowsWithTitle(window_name)[0]
    if w.isActive == False:
        pywinauto.application.Application().connect(handle=w._hWnd).top_window().set_focus()

    base64Frames = []
    for i in range(int(record_seconds * fps)):
        tic = time.perf_counter()
        # make a screenshot
        img = pyautogui.screenshot(region=(w.left, w.top, w.width, w.height))
        display_container.image(img)

        # convert img to numpy array to work with OpenCV
        frame = np.array(img)
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

        # Add delay to ensure frames are captured at the desired fps
        toc = time.perf_counter()
        while (toc - tic) < 1/fps:
            toc = time.perf_counter()
    
    return base64Frames


def frames_to_story(base64Frames, prompt):
    PROMPT_MESSAGES = [
        {
            "role": "user",
            "content": [
                prompt,
                *map(lambda x: {"image": x, "resize": 768},
                     base64Frames[0::10]),
            ],
        },
    ]
    params = {
        "model": "gpt-4-vision-preview",
        "messages": PROMPT_MESSAGES,
        "max_tokens": 500,
    }

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    result = client.chat.completions.create(**params)
    print(result.choices[0].message.content)
    return result.choices[0].message.content


def text_to_audio(text):
    response = requests.post(
        "https://api.openai.com/v1/audio/speech",
        headers={
            "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
        },
        json={
            "model": "tts-1",
            "input": text,
            "voice": "onyx",
        },
    )

    if response.status_code != 200:
        raise Exception("Request failed with status code")

    # Save audio to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmpfile:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            tmpfile.write(chunk)
        audio_filename = tmpfile.name

    return audio_filename


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
        x,_ = librosa.load(file_path, sr=16000)
        sf.write('tmp.wav', x, 16000)
        time.sleep(get_duration_wave('tmp.wav'))
        audio_container.empty()


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def get_duration_wave(file_path):
   with wave.open(file_path, 'r') as audio_file:
      frame_rate = audio_file.getframerate()
      n_frames = audio_file.getnframes()
      duration = n_frames / float(frame_rate)
      return duration

# Streamlit UI
def main():
    st.set_page_config(page_title="Window Capture", page_icon=":camera_with_flash:")

    st.header("Window Capture :camera_with_flash:")
    window_name = st.text_area(
            "Window Name:", value="Enter the Name of the window you wish to capture.")
    
    prompt = st.text_area(
        "Prompt:", value="Provide exciting commentary!")
    
    record_seconds = 5
    est_word_count = record_seconds * 2
    final_prompt = prompt + f"(The text is meant to be read out over only {record_seconds} seconds long, so make sure the response is less than {est_word_count} words)"
    
    if st.button('Begin!', type="primary") and window_name is not None and final_prompt is not None:
        with st.spinner('Processing...'):
            vision_container = st.empty()
            text_container = st.empty()
            audio_container = st.empty()
            break_botton = st.button('Stop', type="primary")
            while(True):
                base64Frames = window_capture(window_name, 10, record_seconds, vision_container)
                text = frames_to_story(base64Frames, final_prompt)
                text_container.write(text)
                audio_filename = text_to_audio(text)
                autoplay_audio(audio_filename, audio_container)
                if break_botton:
                    break


if __name__ == '__main__':
    main()
