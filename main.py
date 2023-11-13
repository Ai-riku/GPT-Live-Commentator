from dotenv import load_dotenv
from IPython.display import display, Audio
from PIL import Image
from moviepy.editor import VideoFileClip, AudioFileClip

import cv2
import base64
import time
from openai import OpenAI

import io
import os
import requests

import streamlit as st
import tempfile
import numpy as np

load_dotenv()

# Convert video to frames
def video_to_frames(video_file):
    # Save the uploaded video file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmpfile:
        tmpfile.write(video_file.read())
        video_filename = tmpfile.name

    video_duration = VideoFileClip(video_filename).duration

    video = cv2.VideoCapture(video_filename)
    base64Frames = []

    while video.isOpened():
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

    video.release()
    print(len(base64Frames), "frames read.")
    return base64Frames, video_filename, video_duration

# Frame to text
def frames_to_story(base64Frames, prompt):
    PROMPT_MESSAGES = [
        {
            "role": "user",
            "content": [
                prompt,
                *map(lambda x: {"image": x, "resize": 768},
                     base64Frames[0::25]),
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


# Streamlit UI
def main():
    st.set_page_config(page_title="Video voice over", page_icon=":bird:")

    st.header("Video voice over :bird:")
    uploaded_file = st.file_uploader("Choose a file")

    if uploaded_file is not None:
        st.video(uploaded_file)
        prompt = st.text_area(
            "Prompt", value="These are frames of a quick product demo walkthrough. Create a short voiceover script that outline the key actions to take, that can be used along this product demo.")

    if st.button('Generate', type="primary") and uploaded_file is not None:
        with st.spinner('Processing...'):
            base64Frames, video_filename, video_duration = video_to_frames(
                uploaded_file)

            est_word_count = video_duration * 2
            final_prompt = prompt + f"(This video is ONLY {video_duration} seconds long, so make sure the voice over MUST be able to be explained in less than {est_word_count} words)"

            # st.write(final_prompt)
            text = frames_to_story(base64Frames, final_prompt)
            st.write(text)

            # # Generate audio from text
            # audio_filename, audio_bytes_io = text_to_audio(text)

            # # Merge audio and video
            # output_video_filename = os.path.splitext(video_filename)[
            #     0] + '_output.mp4'
            # final_video_filename = merge_audio_video(
            #     video_filename, audio_filename, output_video_filename)

            # # Display the result
            # st.video(final_video_filename)

            # # Clean up the temporary files
            # os.unlink(video_filename)
            # os.unlink(audio_filename)
            # os.unlink(final_video_filename)


if __name__ == '__main__':
    main()