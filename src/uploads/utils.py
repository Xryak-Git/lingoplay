import tempfile

import cv2
from fastapi import UploadFile


async def extract_screenshot(upload_file: UploadFile, at_seconds: float = 2.0) -> bytes:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        contents = await upload_file.read()
        tmp.write(contents)
        tmp_path = tmp.name
        upload_file.file.seek(0)


    cap = cv2.VideoCapture(tmp_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_number = int(at_seconds * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    success, frame = cap.read()
    cap.release()

    if not success:
        raise ValueError("Не удалось извлечь кадр из видео.")

    success, buffer = cv2.imencode(".jpg", frame)
    if not success:
        raise ValueError("Не удалось закодировать изображение.")

    return buffer.tobytes()
