from src import config
from src.videos.repository import VideoRepository
from src.videos.service import VideoService


def video_service():
    return VideoService(
        repository=VideoRepository(
            access_key=config.S3_ACCESS_KEY,
            secret_key=config.S3_SECRET_KEY,
            endpoint_url=config.S3_ENDPOINT_URL,
            bucket_name=config.S3_BUCKET_NAME,
        )
    )
