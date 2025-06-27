class BaseAppError(Exception):
    """Базовая ошибка приложения."""


class RepositoryError(BaseAppError):
    """Базовая ошибка репозитория."""


class UniqueConstraintViolation(RepositoryError):
    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value
        super().__init__(f"Field '{field}' must be unique. Got duplicate: '{value}'.")


class DatabaseCommitError(RepositoryError):
    """Ошибка при коммите в базу данных."""


class RecordNotFound(RepositoryError):
    def __init__(self, model_name: str):
        super().__init__(f"{model_name} not found.")


class AlreadyExistsError(Exception):
    def __init__(self, model, field: str, value: str):
        self.field = field
        self.value = value
        super().__init__(f"{model} with {field}='{value}' already exists.")
