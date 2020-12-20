from typing import Optional, List
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import joinedload, load_only

from sqlalchemy import and_

from app.shared.db import db

from app.shared.repository import RepositoryBase

from app.models import QuestionResponse, QuestionResponseStatus
from app.models import Question
from app.models import Response


class QuestionRepository(RepositoryBase):
    model = Question

    def get(self, label: str):
        return self.model.query.filter(self.model.label == label).scalar()

    def get_random_for_quiz(
        self, nbr: int, exclude_questions_ids: Optional[List[id]] = None
    ):
        query = self.model.query.join(self.model.responses).options(
            joinedload(self.model.responses)
            .load_only()
            .options(joinedload(QuestionResponse.response).load_only("label", "uuid"))
        )

        if exclude_questions_ids != None:
            query = query.filter(self.model.id.notin_(exclude_questions_ids))

        return query.order_by(func.random()).limit(nbr).all()

    def check_answer(self, question_uuid: str, response_uuid: str):
        return db.session.query(
            self.model.query.join(self.model.responses, QuestionResponse.response)
            .filter(
                self.model.uuid == question_uuid,
                self.model.responses.any(
                    and_(
                        Response.uuid == response_uuid,
                        QuestionResponse.status == QuestionResponseStatus.CORRECT,
                    )
                ),
            )
            .exists()
        ).scalar()
