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
