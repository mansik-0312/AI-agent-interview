import cv2


def analyze_video(video_path):

    face_detector = cv2.CascadeClassifier(
        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml"
    )

    cap = cv2.VideoCapture(video_path)

    total_frames = 0
    face_frames = 0

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        total_frames += 1

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = face_detector.detectMultiScale(
            gray,
            1.3,
            5
        )

        if len(faces) > 0:
            face_frames += 1

    cap.release()

    face_visible = 0

    if total_frames > 0:
        face_visible = (
            face_frames /
            total_frames
        ) * 100

    return {
        "face_visible": round(
            face_visible,
            2
        )
    }