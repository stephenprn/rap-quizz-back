from typing import Optional, List

from sqlalchemy import desc, asc

from app.shared.repository import RepositoryBase
from app.models import Song


class SongRepository(RepositoryBase):
    model = Song

    def _filter_query(
        self,
        query,
        filter_artist_id_in: List[int] = None,
        filter_out_null_genius_pageviews: bool = False,
        *args,
        **kwargs
    ):
        query = self._filter_query_common(query, *args, **kwargs)

        if filter_artist_id_in is not None:
            query = query.filter(self.model.artist_id.in_(filter_artist_id_in))

        if filter_out_null_genius_pageviews:
            query = query.filter(self.model.genius_pageviews is not None)

        return query

    def _sort_query(
        self,
        query,
        # true: asc, false: desc
        order_genius_pageviews: Optional[bool] = None,
        *args,
        **kwargs
    ):
        query = self._sort_query_common(query, *args, **kwargs)

        if order_genius_pageviews is not None:
            if order_genius_pageviews:
                order_func = asc
            else:
                order_func = desc

            query = query.order_by(order_func(self.model.genius_pageviews))

        return query
