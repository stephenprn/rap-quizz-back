from typing import List

from sqlalchemy.orm.query import Query

from app.shared.repository import RepositoryBase

from app.models import Artist


class ArtistRepository(RepositoryBase):
    model = Artist

    def _filter_query(
        self, query, filter_genius_id_in: List[int] = None, *args, **kwargs
    ) -> Query:
        query = self._filter_query_common(query, *args, **kwargs)

        if filter_genius_id_in is not None:
            query = query.filter(self.model.genius_id.in_(filter_genius_id_in))

        return query
