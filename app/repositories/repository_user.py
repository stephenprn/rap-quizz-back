
from app.shared.repository import RepositoryBase

from app.models import User


class UserRepository(RepositoryBase):
    model = User
