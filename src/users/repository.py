from src.repository import AlchemyRepository
from src.users.models import LingoplayUsers


class UserRepository(AlchemyRepository):
    model = LingoplayUsers
