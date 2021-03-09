from sqlalchemy.orm import joinedload, load_only
from sqlalchemy import desc
from typing import List

from app.shared.db import db
from app.shared.repository import RepositoryBase

from app.models import UserQuiz, User, Quiz, UserQuizStatus, QuizStatus


class UserQuizRepository(RepositoryBase):
    model = UserQuiz

    def get_by_quiz_id_user_id(self, quiz_id: int, user_id: int) -> UserQuiz:
        return self.model.query.filter(
            UserQuiz.quiz_id == quiz_id, UserQuiz.user_id == user_id
        ).options(
            load_only("status", "creation_date").options(
                joinedload(UserQuiz.user).load_only("username", "uuid")
            )
        ).first()

    def count_participating_by_quiz_id(self, quiz_id: int) -> int:
        return self.model.query.filter(UserQuiz.quiz_id == quiz_id, UserQuiz.user_leaved_quiz_status == None).count()

    def get_by_quiz_uuid_user_id(self, quiz_uuid: str, user_id: int) -> UserQuiz:
        return (
            self.model.query.join(self.model.quiz)
            .filter(Quiz.uuid == quiz_uuid, UserQuiz.user_id == user_id)
            .first()
        )

    def get_by_quiz_uuid_user_uuid(self, quiz_uuid: str, user_uuid: str) -> UserQuiz:
        return (
            self.model.query.join(self.model.quiz)
            .join(self.model.user)
            .filter(Quiz.uuid == quiz_uuid, User.uuid == user_uuid)
            .first()
        )

    def get_by_user_id(self, user_id: int, nbr_results: int, page_nbr: int) -> List[UserQuiz]:
        query = self.model.query.join(self.model.quiz).options(
            joinedload(self.model.quiz)
            .load_only("nbr_questions", "question_duration", "status", "uuid")
        ).filter(
            self.model.user_id == user_id,
            Quiz.hidden == False
        ).order_by(
            desc(self.model.creation_date)
        )

        return self._paginate(query, nbr_results=nbr_results, page_nbr=page_nbr, with_nbr_results=True)

    def set_status(self, quiz_uuid: str, user_uuid: str, status: UserQuizStatus):
        user_quiz = self.get_by_quiz_uuid_user_uuid(quiz_uuid, user_uuid)
        user_quiz.status = status
        db.session.commit()
