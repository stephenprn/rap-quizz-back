from sqlalchemy import and_
from sqlalchemy.orm import joinedload, load_only

from app.shared.repository import RepositoryBase

from app.models import ResponseType, Response
from app.models import Question
from app.models import Quiz
from app.models import QuizQuestion, QuestionResponse, QuizQuestionResponse


class QuizQuestionRepository(RepositoryBase):
    model = QuizQuestion

    def get(self, quiz_url: str, question_index: int):
        return (
            self.model.query.join(self.model.quiz)
            .join(self.model.question)
            .options(
                joinedload(self.model.question)
                .joinedload(Question.responses)
                .load_only()
                .options(
                    joinedload(QuestionResponse.response).load_only("label", "uuid")
                ),
                joinedload(self.model.responses_false).options(
                    joinedload(QuizQuestionResponse.response).load_only("label", "uuid")
                ),
            )
            .filter(Quiz.url == quiz_url, self.model.question_index == question_index)
            .first()
        )
