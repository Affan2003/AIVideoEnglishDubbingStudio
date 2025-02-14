import os
import subprocess
import whisper
from gtts import gTTS
import streamlit as st

# Install required packages
required_libraries = ["whisper", "gTTS", "streamlit"]
for lib in required_libraries:
    try:
        __import__(lib)
    except ImportError:
        subprocess.run(["pip", "install", lib])

# Streamlit UI
st.set_page_config(page_title="AI Video English Dubbing Studio", page_icon="🎥", layout="centered")
st.title("🎬 AI Video English Dubbing Studio")
st.markdown("**Transform non-English videos into English-dubbed content with ease!**")

# Upload video file
uploaded_file = st.file_uploader("📤 Upload a video file (Supported formats: MP4, MOV, AVI)", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    st.write("📽️ Processing the video, please wait...")

    with open("temp_video.mp4", "wb") as f:
        f.write(uploaded_file.read())
    temp_video_path = "temp_video.mp4"

    # Step 1: Extract audio using FFmpeg
    audio_file_path = "temp_audio.wav"
    st.write("🔊 Extracting audio from the video...")
    subprocess.run(["ffmpeg", "-i", temp_video_path, "-q:a", "0", "-map", "a", audio_file_path])

    # Step 2: Transcribe audio using Whisper
    st.write("📝 Transcribing audio using Whisper...")
    model = whisper.load_model("base")
    result = model.transcribe(audio_file_path, language="en")
    transcription = result["text"]

    # Step 3: Generate English audio using gTTS
    st.write("🎤 Generating English audio from the transcription...")
    tts = gTTS(transcription, lang="en")
    english_audio_path = "english_audio.mp3"
    tts.save(english_audio_path)

    # Step 4: Replace original audio with English audio using FFmpeg
    st.write("🔄 Replacing original audio with English audio...")
    output_video_path = "output_video.mp4"
    ffmpeg_command = [
        "ffmpeg",
        "-i", temp_video_path,
        "-i", english_audio_path,
        "-map", "0:v:0",  # Map video from the first input
        "-map", "1:a:0",  # Map audio from the second input
        "-c:v", "copy",
        "-c:a", "aac",
        "-strict", "experimental",
        output_video_path
    ]

    process = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Check if the output video was created successfully
    if process.returncode == 0 and os.path.exists(output_video_path):
        st.success("✅ Processing completed. Here is your video with English dubbing:")
        st.video(output_video_path)
        st.download_button("⬇️ Download Your English-Dubbed Video", data=open(output_video_path, "rb"), file_name="english_dubbed_video.mp4")
    else:
        st.error("❌ Failed to generate the output video. Check the error log below:")
        st.code(process.stderr.decode())
