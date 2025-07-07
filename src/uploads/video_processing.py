import os
from tempfile import TemporaryDirectory

import cv2
import easyocr

from src.s3 import AbstractS3Repository
from src.uploads.models import Videos
from src.uploads.schemas import LingoplayImage

import structlog

logger = structlog.get_logger()

class VideoProcessor:
    def __init__(self, s3_repo: AbstractS3Repository):
        self._s3_repo = s3_repo
        self._temp_dir = TemporaryDirectory(delete=False)
        self._frames_dir = self._temp_dir.name
        self._reader = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # self._temp_dir.cleanup()
        pass

    async def process_video_from_s3(self, video: Videos, lang: str = "en") -> list[LingoplayImage]:
        # Скачиваем видео
        video_path = await self._s3_repo.download_to_tempfile(video.s3_key)
        logger.info(f"Downloaded {video_path}")

        # Извлекаем кадры
        await self.extract_frames_from_video(video_path)

        # Извлекаем текст
        results = await self.extract_text_from_frames(video, lang)

        return results

    async def extract_frames_from_video(self, video_path: str, fps_interval: int = 1):
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if not fps or fps == 0.0:
            logger.warning("FPS not found, using default = 25")
            fps = 25

        frame_interval = int(fps * fps_interval)
        frame_count = 0
        saved_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or frame is None or frame.size == 0:
                break

            if frame_count % frame_interval == 0:
                frame_path = os.path.join(self._frames_dir, f"frame_{saved_count:04d}.jpg")
                logger.info(f"Saving frame to {frame_path}, shape={frame.shape}")
                cv2.imwrite(frame_path, frame)
                saved_count += 1

            frame_count += 1

        cap.release()


    async def extract_text_from_frames(self, video: Videos, lang: str = "en") -> list[LingoplayImage]:
        if self._reader is None:
            self._reader = easyocr.Reader([lang], gpu=True)

        results = []

        for filename in sorted(os.listdir(self._frames_dir)):
            if filename.endswith(".jpg"):
                path = os.path.join(self._frames_dir, filename)
                ocr_result = self._reader.readtext(path, detail=0)
                combined_text = " ".join(ocr_result).strip()

                results.append(LingoplayImage(video=video, path=path, text=combined_text))

        print(results)
        return results

