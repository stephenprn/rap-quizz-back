from sqlalchemy.orm import joinedload

from app.shared.repository import RepositoryBase

from app.models import UserQuiz


class UserQuizRepository(RepositoryBase):
    model = UserQuiz
