from sqlalchemy.orm import joinedload

from app.shared.db import db
from app.shared.repository import RepositoryBase

from app.models import UserQuiz, User, Quiz, UserQuizStatus


class UserQuizRepository(RepositoryBase):
    model = UserQuiz

    def get_by_quiz_id_user_id(self, quiz_id: int, user_id: int) -> UserQuiz:
        return self.model.query.filter(
            UserQuiz.quiz_id == quiz_id,
            UserQuiz.user_id == user_id
        ).first()

    def get_by_quiz_uuid_user_id(self, quiz_uuid: str, user_id: int) -> UserQuiz:
        return self.model.query.join(self.model.quiz).filter(
            Quiz.uuid == quiz_uuid,
            UserQuiz.user_id == user_id
        ).first()

    def get_by_quiz_uuid_user_uuid(self, quiz_uuid: str, user_uuid: str) -> UserQuiz:
        return self.model.query.join(self.model.quiz).join(self.model.user).filter(
            Quiz.uuid == quiz_uuid,
            User.uuid == user_uuid
        ).first()

    def set_status(self, quiz_uuid: str, user_uuid: str, status: UserQuizStatus):
        user_quiz = self.get_by_quiz_uuid_user_uuid(quiz_uuid, user_uuid)
        user_quiz.status = status
        db.session.commit()
