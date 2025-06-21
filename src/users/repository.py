from src.repository import AlchemyRepository
from src.users.models import LingoplayUser


class UserRepository(AlchemyRepository):
    model = LingoplayUser
