from typing import Optional, List

from app.shared.db import db
from app.shared.model import ModelCommon

from sqlalchemy.orm.query import Query


class RepositoryBase:
    __abstract__ = True

    model = None

    def get(self, id, *agrs, **kwargs) -> ModelCommon:
        return self.model.query.filter(id == id).one()

    def list(self, id, *agrs, **kwargs) -> List[ModelCommon]:
        query = self.model.query

        query = self._paginate(
            query, nbr_results=kwargs.get("nbr_results"), page=kwargs.get("page")
        )

        return query.all()

    def count(self, *args, **kwargs) -> int:
        return self.model.query.count()

    def add(self, *args, **kwargs) -> None:
        elt = self.model(*args, **kwargs)
        db.session.add(elt)
        db.session.commit()

    def _paginate(
        self,
        query: Query,
        nbr_results: Optional[int] = None,
        page: Optional[int] = None,
    ) -> Query:
        if nbr_results is not None:
            query = query.limit(nbr_results)

        if page is not None:
            query = query.offset(page * nbr_results)

        return query
