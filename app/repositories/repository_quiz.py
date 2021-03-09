from typing import List

from sqlalchemy.orm import joinedload

from app.shared.db import db
from app.shared.repository import RepositoryBase

from app.models import Quiz, UserQuiz, QuizStatus

from app.classes import QuizRoom


class QuizRepository(RepositoryBase):
    model = Quiz

    def get_one_by_url(self, url: str, with_users: bool = False) -> Quiz:
        query = self.model.query.filter(self.model.url == url)

        if with_users:
            query = query.join(self.model.users).options(
                joinedload(self.model.users)
                .load_only("status", "creation_date")
                .options(joinedload(UserQuiz.user).load_only("username", "uuid"))
            )

        return query.first()

    def get_one_by_uuid(self, uuid: str, with_users: bool = False) -> Quiz:
        query = self.model.query.filter(self.model.uuid == uuid)

        if with_users:
            query = query.join(self.model.users).options(
                joinedload(self.model.users)
                .load_only("status", "creation_date")
                .options(joinedload(UserQuiz.user).load_only("username", "uuid"))
            )

        return query.first()

    def finish_one(self, uuid: str, quiz_room: QuizRoom):
        quiz = self.get_one_by_uuid(uuid, with_users=True)
        quiz.status = QuizStatus.FINISHED

        for user_quiz in quiz.users:
            player = quiz_room.get_player(user_quiz.user.uuid)
            user_quiz.score = player.score
            user_quiz.user_leaved_quiz_status = QuizStatus.FINISHED
            
        db.session.commit()

    def set_status_by_uuid(self, uuid: str, status: QuizStatus) -> None:
        quiz = self.get_one_by_uuid(uuid)
        quiz.status = status
        db.session.commit()