import os
import shutil
import uuid
import requests


def download_video(recordingUrl: str) -> str:
    """
    Supports:
    1. Local file path
       Example:
       C:/Users/Ashish K/Desktop/video.mp4

    2. Remote URL
       Example:
       https://example.com/video.mp4
    """

    os.makedirs("temp", exist_ok=True)

    print(f"Received path/url: {recordingUrl}")

    # Local file path
    if os.path.isfile(recordingUrl):

        destination = os.path.join(
            "temp",
            f"{uuid.uuid4()}.mp4"
        )

        shutil.copy2(
            recordingUrl,
            destination
        )

        print(
            f"Copied local file to: {destination}"
        )

        return destination

    # Remote URL
    if (
        recordingUrl.startswith("http://")
        or recordingUrl.startswith("https://")
    ):

        destination = os.path.join(
            "temp",
            f"{uuid.uuid4()}.mp4"
        )

        response = requests.get(
            recordingUrl,
            stream=True,
            timeout=60
        )

        response.raise_for_status()

        with open(destination, "wb") as file:

            for chunk in response.iter_content(
                chunk_size=8192
            ):
                if chunk:
                    file.write(chunk)

        print(
            f"Downloaded remote file to: {destination}"
        )

        return destination

    raise ValueError(
        f"Invalid video path or URL: {recordingUrl}"
    )