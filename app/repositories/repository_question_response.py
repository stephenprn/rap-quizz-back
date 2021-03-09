from typing import Optional, List

from sqlalchemy.sql.expression import func
from sqlalchemy import and_
from sqlalchemy.orm import joinedload, load_only

from app.shared.repository import RepositoryBase

from app.models import ResponseType, Response
from app.models import QuestionResponse


class QuestionResponseRepository(RepositoryBase):
    model = QuestionResponse

    def get_random_for_quiz(
        self,
        response_type: ResponseType,
        nbr_results: int,
        exclude_responses_ids: Optional[List[int]],
    ) -> List[QuestionResponse]:
        return (
            self.model.query.join(self.model.response)
            .options(
                load_only(), joinedload(self.model.response).load_only("label", "uuid")
            )
            .filter(
                and_(
                    Response.type == response_type,
                    Response.id.notin_(exclude_responses_ids),
                )
            )
            .order_by(func.random())
            .limit(nbr_results)
            .all()
        )
