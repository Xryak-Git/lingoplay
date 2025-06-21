from src.auth.models import UserTokens
from src.repository import AlchemyRepository


class AuthRepository(AlchemyRepository):
    model = UserTokens
