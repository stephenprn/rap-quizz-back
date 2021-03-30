from typing import Optional, List

from app.shared.db import db
from app.shared.model import ModelCommon

from sqlalchemy.orm.query import Query


class RepositoryBase:
    __abstract__ = True

    model = None

    def get(self, id_, *args, **kwargs) -> ModelCommon:
        return self.model.query.filter(id == id_).one()

    def list_(self, *args, **kwargs) -> List[ModelCommon]:
        query = self.model.query

        query = self._paginate(
            query, nbr_results=kwargs.get("nbr_results"), page_nbr=kwargs.get("page")
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
        page_nbr: Optional[int] = None,
        with_nbr_results: bool = False
    ) -> Query:
        if with_nbr_results:
            res = query.paginate(
                page=page_nbr,
                per_page=nbr_results,
                error_out=False
            )
            return {
                "total": res.total,
                "data": res.items
            }

        if nbr_results is not None:
            query = query.limit(nbr_results)

        if page_nbr is not None:
            query = query.offset(page_nbr * nbr_results)

        return query
