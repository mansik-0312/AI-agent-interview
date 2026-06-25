import os

# Add FFmpeg to PATH before importing whisper
FFMPEG_DIR = r"C:\Users\Ashish K\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin"

os.environ["PATH"] = (
    FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")
)

from moviepy import VideoFileClip
import whisper
import shutil


model = whisper.load_model("base")


def extract_audio(video_path):

    audio_path = video_path.replace(
        ".mp4",
        ".wav"
    )

    video = VideoFileClip(video_path)

    video.audio.write_audiofile(
        audio_path
    )

    return audio_path


def transcribe_audio(audio_path):

    print("Audio Exists:", os.path.exists(audio_path))
    print("Audio Path:", audio_path)

    result = model.transcribe(
        audio_path
    )

    return result["text"]


def calculate_speaking_speed(
        transcript,
        duration_seconds
):

    words = len(
        transcript.split()
    )

    minutes = (
        duration_seconds / 60
    )

    if minutes == 0:
        return 0

    return round(
        words / minutes,
        2
    )


FILLER_WORDS = [
    "um",
    "uh",
    "actually",
    "basically",
    "like",
    "you know"
]


def count_fillers(text):

    words = text.lower().split()

    count = 0

    for word in words:

        if word in FILLER_WORDS:
            count += 1

    return count