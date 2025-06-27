

class VideoAlreadyUploadedError(Exception):
    def __init__(self, name: str):
        super().__init__(f"Видео с названием '{name}' уже загружено")
