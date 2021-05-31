from typing import List, Optional

from sqlalchemy.orm import joinedload

from app.shared.repository import RepositoryBase

from app.models import Question
from app.models import Quiz
from app.models import QuizQuestion, QuestionResponse, QuizQuestionResponse


class QuizQuestionRepository(RepositoryBase):
    model = QuizQuestion

    def _filter_query(self,
                      query,
                      filter_quiz_uuid_in: Optional[List[str]] = None,
                      *args,
                      **kwargs):
        if filter_quiz_uuid_in is not None:
            query = query.join(self.model.quiz).filter(
                Quiz.uuid.in_(filter_quiz_uuid_in)
            )

        return query

    def _load_only(
            self,
            query,
            load_only_response_label: Optional[bool] = False,
            *args,
            **kwargs):
        if load_only_response_label:
            query = query.options(
                joinedload(
                    self.model.question) .load_only(
                    "label",
                    "type",
                    "uuid",
                    "picture") .joinedload(
                    Question.responses) .load_only("status") .options(
                    joinedload(
                        QuestionResponse.response).load_only(
                            "label",
                            "uuid")),
                joinedload(
                    self.model.responses_false).options(
                    joinedload(
                        QuizQuestionResponse.response).load_only(
                        "label",
                        "uuid")),
            )

        return query
