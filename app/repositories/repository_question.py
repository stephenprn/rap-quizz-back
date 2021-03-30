from typing import Optional, List
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import joinedload, load_only

from sqlalchemy import and_, desc

from app.shared.db import db
from app.shared.repository import RepositoryBase
from app.models import QuestionResponse, QuestionResponseStatus, Question, ResponseType, QuestionSubType, Response


class QuestionRepository(RepositoryBase):
    model = Question

    def get(self, label: str = None, uuid: str = None, type_: ResponseType = None, sub_type: QuestionSubType = None, true_response_id: int = None) -> Question:
        query = self.model.query

        if label is not None:
            query = query.filter(self.model.label == label)

        if type_ is not None:
            query = query.filter(self.model.type == type_)

        if sub_type is not None:
            query = query.filter(self.model.sub_type == sub_type)

        if uuid is not None:
            query = query.filter(self.model.uuid == uuid)

        if true_response_id is not None:
            query = query.join(self.model.responses).filter(and_(QuestionResponse.response_id ==
                                                                 true_response_id, QuestionResponse.status == QuestionResponseStatus.CORRECT,))

        return query.scalar()

    def get_random_for_quiz(
        self, nbr: int, exclude_questions_ids: Optional[List[id]] = None
    ) -> List[Question]:
        query = self.model.query.filter(self.model.hidden == False).join(self.model.responses).options(
            joinedload(self.model.responses)
            .load_only()
            .options(joinedload(QuestionResponse.response).load_only("label", "uuid"))
        )

        if exclude_questions_ids != None:
            query = query.filter(self.model.id.notin_(exclude_questions_ids))

        return query.order_by(func.random()).limit(nbr).all()

    def check_answer(self, question_uuid: str, response_uuid: str) -> bool:
        return db.session.query(
            self.model.query.join(self.model.responses,
                                  QuestionResponse.response)
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

    def list_(self, nbr_results: int, page_nbr: int, hidden: bool = None):
        query = self.model.query

        if hidden is not None:
            query = query.filter(
                self.model.hidden == hidden
            )
        
        query = query.order_by(desc(self.model.creation_date))

        return self._paginate(query, nbr_results=nbr_results, page_nbr=page_nbr, with_nbr_results=True)
