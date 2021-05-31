from sqlalchemy.orm import joinedload, load_only
from typing import List, Optional

from app.shared.repository import RepositoryBase

from app.models import Quiz, UserQuiz


class UserQuizRepository(RepositoryBase):
    model = UserQuiz

    def _filter_query(
        self,
        query,
        filter_quiz_id_in: List[int] = None,
        filter_quiz_uuid_in: List[str] = None,
        filter_user_id_in: List[int] = None,
        filter_user_uuid_in: List[str] = None,
        filter_hidden: bool = None,
        filter_null_user_leaved_quiz_status: Optional[bool] = None,
        *args,
        **kwargs
    ):
        if filter_quiz_id_in is not None:
            query = query.filter(self.model.quiz_id.in_(filter_quiz_id_in))

        if filter_quiz_uuid_in is not None:
            query = query.join(self.model.quiz).filter(
                Quiz.uuid.in_(filter_quiz_uuid_in)
            )

        if filter_user_id_in is not None:
            query = query.filter(self.model.user_id.in_(filter_user_id_in))

        if filter_user_uuid_in is not None:
            query = query.join().filter(self.model.user_id.in_(filter_user_uuid_in))

        if filter_null_user_leaved_quiz_status is not None:
            query = query.filter(self.model.user_leaved_quiz_status is None)

        if filter_hidden is not None:
            query = query.join(
                self.model.quiz).filter(
                Quiz.hidden == filter_hidden)

        return query

    def _load_only(
        self,
        query,
        load_only_status_username: Optional[bool] = None,
        load_only_quiz_infos: Optional[bool] = None,
        *args,
        **kwargs
    ):
        if load_only_status_username:
            query = query.options(
                load_only("status", "creation_date").options(
                    joinedload(UserQuiz.user).load_only("username", "uuid")
                )
            )

        if load_only_quiz_infos:
            query = query.options(
                joinedload(self.model.quiz).load_only(
                    "nbr_questions", "question_duration", "status", "uuid"
                )
            )

        return query
