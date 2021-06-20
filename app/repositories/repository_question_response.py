from typing import Optional, List

from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.orm.query import Query

from app.shared.repository import RepositoryBase

from app.models import ResponseType, Response
from app.models import QuestionResponse


class QuestionResponseRepository(RepositoryBase):
    model = QuestionResponse

    def _load_only(
            self,
            query,
            load_only_response_label: Optional[bool] = False,
            *args,
            **kwargs) -> Query:
        if load_only_response_label:
            query = query.join(
                self.model.response).options(
                load_only(),
                joinedload(
                    self.model.response).load_only(
                    "label",
                    "uuid"))

        return query

    def _filter_query(
        self,
        query,
        filter_response_type_in: Optional[List[ResponseType]] = None,
        filter_response_id_not_in: Optional[List[int]] = None,
        *args,
        **kwargs
    ) -> Query:
        if filter_response_type_in is not None:
            query = query.join(self.model.response).filter(
                Response.type.in_(filter_response_type_in)
            )

        if filter_response_id_not_in is not None:
            query = query.join(self.model.response).filter(
                Response.id.notin_(filter_response_id_not_in)
            )

        return query
