from typing import Optional, List
from sqlalchemy.sql.expression import func

from app.shared.repository import RepositoryBase

from app.models import Response, ResponseType


class FilterLabel:
    label: str
    ignore_case: bool

    def __init__(self, label: str, ignore_case: bool = False):
        self.label = label
        self.ignore_case = ignore_case


class ResponseRepository(RepositoryBase):
    model = Response

    def list_(self, *args, **kwargs):
        query = self.model.query

        query = self._filter_query(query, *args, **kwargs)
        query = self._sort_query(query, *args, **kwargs)
        query = self._paginate(query, *args, **kwargs)

        return query.all()

    def get(self, *args, **kwargs):
        results = self.list_(*args, **kwargs)

        return results[0] if results else None

    def _filter_query(
        self,
        query,
        filter_label: Optional[FilterLabel] = None,
        filter_type_in: Optional[List[ResponseType]] = None,
        filter_uuid_in: Optional[List[str]] = None,
        filter_search_text: Optional[str] = None,
        filter_id_not_in: Optional[List[int]] = None,
        filter_uuid_not_in: Optional[List[str]] = None,
        *args,
        **kwargs
    ):
        if filter_label is not None:
            if filter_label.ignore_case:
                query = query.filter(
                    self.model.label.ilike(filter_label.label)
                )
            else:
                query = query.filter(
                    self.model.label == filter_label.label
                )

        if filter_type_in is not None:
            query = query.filter(
                self.model.type.in_(filter_type_in)
            )

        if filter_uuid_in is not None:
            query = query.filter(
                self.model.uuid.in_(filter_uuid_in)
            )

        if filter_search_text is not None:
            query = query.filter(
                self.model.label.ilike(f"%{filter_search_text}%")
            )

        if filter_id_not_in is not None:
            query = query.filter(
                self.model.id.notin_(filter_id_not_in)
            )

        if filter_uuid_not_in is not None:
            query = query.filter(
                self.model.uuid.notin_(filter_uuid_not_in)
            )
            
        return query

    def _sort_query(
        self,
        query,
        order_random: Optional[bool] = False,
        *args,
        **kwargs
    ):
        if order_random:
            query = query.order_by(func.random())

        return query
