from ultralytics import YOLO

model = YOLO(
    "yolov8n.pt"
)

import cv2


def detect_multiple_persons(
    video_path: str
):

    cap = cv2.VideoCapture(
        video_path
    )

    frame_count = 0

    max_person_count = 0

    multiple_person_frames = 0

    while True:

        success, frame = cap.read()

        if not success:
            break

        frame_count += 1

        # Process every 30th frame
        if frame_count % 30 != 0:
            continue

        results = model(
            frame,
            verbose=False
        )

        person_count = 0

        for box in results[0].boxes:

            class_id = int(
                box.cls[0]
            )

            class_name = (
                model.names[
                    class_id
                ]
            )

            if class_name == "person":

                person_count += 1

        max_person_count = max(
            max_person_count,
            person_count
        )

        if person_count > 1:

            multiple_person_frames += 1

    cap.release()

    return {
        "multiple_person_detected":
            multiple_person_frames > 0,

        "max_person_count":
            max_person_count,

        "multiple_person_frames":
            multiple_person_frames
    }


def detect_suspicious_objects(
    video_path: str
):

    cap = cv2.VideoCapture(
        video_path
    )

    frame_count = 0

    detected_objects = set()

    suspicious = [
        "cell phone",
        "book",
        "laptop"
    ]

    while True:

        success, frame = cap.read()

        if not success:
            break

        frame_count += 1

        if frame_count % 60 != 0:
            continue

        results = model(
            frame,
            verbose=False
        )

        for box in results[0].boxes:

            class_id = int(
                box.cls[0]
            )

            object_name = (
                model.names[
                    class_id
                ]
            )

            if object_name in suspicious:

                detected_objects.add(
                    object_name
                )

    cap.release()

    return {
        "suspicious_objects":
            list(detected_objects)
    }


