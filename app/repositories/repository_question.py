from typing import Optional, List
from sqlalchemy.orm import joinedload

from sqlalchemy import and_, or_

from app.shared.db import db
from app.shared.repository import RepositoryBase
from app.models import (
    QuestionResponse,
    QuestionResponseStatus,
    Question,
    ResponseType,
    QuestionSubType,
    Response,
)
from app.utils.utils_query import FilterLabel


class QuestionRepository(RepositoryBase):
    model = Question

    def _filter_query(
        self,
        query,
        filter_label: Optional[FilterLabel] = None,
        filter_uuid_in: Optional[List[str]] = None,
        filter_type_in: Optional[List[ResponseType]] = None,
        filter_sub_type_in: Optional[List[QuestionSubType]] = None,
        filter_true_response_id_in: Optional[List[int]] = None,
        filter_hidden: Optional[bool] = None,
        filter_responses_hidden: Optional[bool] = None,
        filter_question_id_not_in: Optional[List[int]] = None,
        *args,
        **kwargs
    ):
        query = self._filter_query_common(query, *args, **kwargs)

        if filter_label is not None:
            if filter_label.ignore_case:
                query = query.filter(
                    self.model.label.ilike(
                        filter_label.label))
            else:
                query = query.filter(self.model.label == filter_label.label)

        if filter_uuid_in is not None:
            query = query.filter(self.model.uuid.in_(filter_uuid_in))

        if filter_type_in is not None:
            query = query.filter(self.model.type.in_(filter_type_in))

        if filter_sub_type_in is not None:
            query = query.filter(self.model.sub_type.in_(filter_sub_type_in))

        if filter_true_response_id_in is not None:
            query = query.join(
                self.model.responses).filter(
                and_(
                    QuestionResponse.response_id.in_(filter_true_response_id_in),
                    QuestionResponse.status == QuestionResponseStatus.CORRECT,
                ))

        if filter_hidden is not None:
            query = query.filter(self.model.hidden == filter_hidden)

        if filter_responses_hidden is not None:
            query = (
                query.outerjoin(self.model.responses)
                .outerjoin(QuestionResponse.response)
                .filter(
                    or_(
                        Response.hidden == filter_responses_hidden,
                        self.model.responses is None,
                    )
                )
            )

        if filter_question_id_not_in is not None:
            query = query.filter(
                self.model.id.notin_(filter_question_id_not_in))

        return query

    def _load_only(
        self,
        query,
        load_only_response_label: Optional[bool] = False,
        load_full_response: Optional[bool] = False,
        *args,
        **kwargs
    ):
        if load_full_response:
            query = query.outerjoin(
                self.model.responses).options(
                joinedload(
                    self.model.responses) .load_only("status") .options(
                    joinedload(
                        QuestionResponse.response).load_only(
                        "label",
                        "uuid")))

        if load_only_response_label:
            query = query.outerjoin(
                self.model.responses).options(
                joinedload(
                    self.model.responses) .load_only() .options(
                    joinedload(
                        QuestionResponse.response).load_only(
                        "label",
                        "uuid")))

        return query

    def check_answer(self, question_uuid: str, response_uuid: str) -> bool:
        return db.session.query(
            self.model.query.join(
                self.model.responses,
                QuestionResponse.response) .filter(
                self.model.uuid == question_uuid,
                self.model.responses.any(
                    and_(
                        Response.uuid == response_uuid,
                        QuestionResponse.status == QuestionResponseStatus.CORRECT,
                    )),
            ) .exists()).scalar()
