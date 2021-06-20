from app.utils.utils_query import FilterInt, FilterText
from typing import Optional, List

from sqlalchemy.sql.expression import func
from sqlalchemy.orm.query import Query
from sqlalchemy import desc, asc

from app.shared.db import db


class RepositoryBase:
    __abstract__ = True

    model = None

    def list_(self, *args, **kwargs):
        query = self.model.query

        query = self._filter_query(query, *args, **kwargs)
        query = self._load_only(query, *args, **kwargs)
        query = self._sort_query(query, *args, **kwargs)

        return self._execute(query, *args, **kwargs)

    def count(self, *args, **kwargs) -> int:
        query = self.model.query

        query = self._filter_query(query, *args, **kwargs)
        query = self._load_only(query, *args, **kwargs)
        query = self._sort_query(query, *args, **kwargs)

        return query.count()

    def get(self, *args, **kwargs):
        results = self.list_(*args, **kwargs)

        return results[0] if results else None

    def add(self, *args, **kwargs) -> None:
        elt = self.model(*args, **kwargs)
        db.session.add(elt)
        db.session.commit()

    def _filter_query(self, query, *args, **kwargs):
        return self._filter_query_common(query, *args, **kwargs)

    def _load_only(self, query, *args, **kwargs):
        return query

    def _sort_query(self, query, *args, **kwargs):
        return self._sort_query_common(query, *args, **kwargs)

    # true: asc, false: desc
    def _sort_query_common(
        self,
        query,
        order_creation_date: Optional[bool] = None,
        order_update_date: Optional[bool] = None,
        order_random: Optional[bool] = None,
        *args,
        **kwargs,
    ):
        if order_random:
            query = query.order_by(func.random())

        if order_creation_date is not None:
            if order_creation_date:
                order_func = asc
            else:
                order_func = desc

            query = query.order_by(order_func(self.model.creation_date))

        if order_update_date is not None:
            if order_update_date:
                order_func = asc
            else:
                order_func = desc

            query = query.order_by(order_func(self.model.update_date))

        return query

    def _filter_query_common(
        self,
        query,
        filter_uuid_in: Optional[List[str]] = None,
        filter_id_in: Optional[List[int]] = None,
        *args,
        **kwargs,
    ):
        if filter_uuid_in is not None:
            query = query.filter(self.model.uuid.in_(filter_uuid_in))

        if filter_id_in is not None:
            query = query.filter(self.model.id.in_(filter_id_in))

        return query

    def _apply_filter_int(self, query, field, filter_int: FilterInt) -> Query:
        if filter_int.min_value is not None:
            if filter_int.min_strict:
                query = query.filter(field > filter_int.min_value)
            else:
                query = query.filter(field >= filter_int.min_value)

        if filter_int.max_value is not None:
            if filter_int.max_strict:
                query = query.filter(field < filter_int.max_value)
            else:
                query = query.filter(field <= filter_int.max_value)

        return query

    def _apply_filter_text(
            self,
            query,
            field,
            filter_text: FilterText) -> Query:
        if filter_text.text is None:
            return query

        if filter_text.partial_match:
            content = f"%{filter_text.text}%"
        else:
            content = filter_text.text

        if filter_text.ignore_case:
            query = query.filter(field.ilike(content))
        else:
            query = query.filter(field.like(content))

        return query

    def _execute(
        self,
        query: Query,
        nbr_results: Optional[int] = None,
        page_nbr: Optional[int] = None,
        with_nbr_results: bool = False,
        *args,
        **kwargs,
    ) -> Query:
        if with_nbr_results:
            res = query.paginate(
                page=page_nbr + 1, per_page=nbr_results, error_out=False
            )
            return {"total": res.total, "data": res.items}

        if nbr_results is not None:
            query = query.limit(nbr_results)

        if page_nbr is not None:
            query = query.offset(page_nbr * nbr_results)

        return query.all()
