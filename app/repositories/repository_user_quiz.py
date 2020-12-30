from sqlalchemy.orm import joinedload

from app.shared.repository import RepositoryBase

from app.models import UserQuiz


class UserQuizRepository(RepositoryBase):
    model = UserQuiz

    def get_by_quiz_id_user_id(self, quiz_id: int, user_id: int):
        return self.model.query.filter(
            UserQuiz.quiz_id == quiz_id,
            UserQuiz.user_id == user_id
        ).first()
