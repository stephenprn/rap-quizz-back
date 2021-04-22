from typing import Optional

from app.shared.db import db

from sqlalchemy.orm.query import Query


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
        return query

    def _load_only(self, query, *args, **kwargs):
        return query

    def _sort_query(self, query, *args, **kwargs):
        return self._sort_query_common(query)

    # true: asc, false: desc
    def _sort_query_common(self, query, order_creation_date: Optional[bool] = None, 
                           order_update_date: Optional[bool] = None,
                           order_random: Optional[bool] = None,
                           *args, **kwargs):
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

    def _execute(
        self,
        query: Query,
        nbr_results: Optional[int] = None,
        page_nbr: Optional[int] = None,
        with_nbr_results: bool = False,
        *args,
        **kwargs
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
