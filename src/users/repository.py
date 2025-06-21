from src.repository import AlchemyRepository
from src.users.models import LingoplayUser


class UserRepository(AlchemyRepository):
    model = LingoplayUser

    def create_one(self, data):
        data["password"] = bytes(data.get("password"), "utf-8")
        return super().create_one(data)
