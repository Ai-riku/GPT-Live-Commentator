# AI Live Commentary

This application is designed to capture frames of a specified window, continuously generate audio narration/commentary from the captured frames using an AI model, and provide a user interface for interaction.

## Features
- **Window Capture**: Captures frames of a specified window to give the AI context.
- **Story Generation**: Generates a story from the captured frames using OpenAI's `gpt-4-vision-preview` Model.
- **Audio Conversion**: Converts the generated story to audio using an OpenAI's TTS service.
- **Streamlit UI**: Provides a user interface for interacting with the script.

## Usage
1. Requirements: Install the necessary Python packages by running `pip install -r requirements.txt`. Install the custom display capture component with `cd packages` and `pip install streamlit_webrtc_display_capture-0.47.1.tar.gz`
2. Add your OpenAI API key: Create a `.env` file in the root directory and add your key with `OPENAI_API_KEY = "Your Key"`.
3. (Optional) Setup a TURN server and add the parameters inside the `.env` file: `ICE_SERVER = "Ice Server"; USER = "User"; PASS = "Password"` each in their seperate lines.
    A fallback option is provided where the script will use a free STUN server from google, which may or may not work in some network environments.
4. Run the script in root folder: `streamlit run main.py`.

### Streamlit UI
- Select the window to capture.
- Choose a voice for the narration.
- Enter a prompt for generating the story.
- Click the "Begin!" button to start capturing frames and generating commentary.
- Click the "Stop" button to end the process.

## Dependencies
The script depends on the following Python packages:
- cv2
- pyautogui
- time
- base64
- os
- requests
- tempfile
- wave
- librosa
- streamlit
- numpy
- soundfile
- openai
- dotenv
- streamlit_webrtc_display_capture (modified version from streamlit_webrtc)

## Note
- Currently Windows is the only supported platform
- Provide appropriate prompts for generating the desired narration.

For further details, refer to the `main.py` file for the complete code.

---

This README provides an overview of the functionality and usage of the `main.py` script. If there are additional details or specific instructions that should be included, please let me know.
