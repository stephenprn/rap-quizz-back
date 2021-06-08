from typing import Optional, List

from app.shared.repository import RepositoryBase

from app.models import Response, ResponseType
from app.utils.utils_query import FilterLabel


class ResponseRepository(RepositoryBase):
    model = Response

    def _filter_query(
        self,
        query,
        filter_label: Optional[FilterLabel] = None,
        filter_hidden: Optional[bool] = None,
        filter_type_in: Optional[List[ResponseType]] = None,
        filter_search_text: Optional[str] = None,
        filter_id_not_in: Optional[List[int]] = None,
        filter_uuid_not_in: Optional[List[str]] = None,
        *args,
        **kwargs,
    ):
        query = self._filter_query_common(query, *args, **kwargs)

        if filter_label is not None:
            if filter_label.ignore_case:
                query = query.filter(
                    self.model.label.ilike(
                        filter_label.label))
            else:
                query = query.filter(self.model.label == filter_label.label)

        if filter_type_in is not None:
            query = query.filter(self.model.type.in_(filter_type_in))

        if filter_search_text is not None:
            query = query.filter(
                self.model.label.ilike(f"%{filter_search_text}%"))

        if filter_id_not_in is not None:
            query = query.filter(self.model.id.notin_(filter_id_not_in))

        if filter_uuid_not_in is not None:
            query = query.filter(self.model.uuid.notin_(filter_uuid_not_in))

        if filter_hidden is not None:
            query = query.filter(self.model.hidden == filter_hidden)

        return query
