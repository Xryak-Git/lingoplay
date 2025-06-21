from src.users.repository import UserRepository
from src.users.service import UsersService


def user_service():
    return UsersService(repository=UserRepository())
