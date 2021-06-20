from typing import Optional, List

from sqlalchemy import desc, asc
from sqlalchemy.orm.query import Query

from app.shared.repository import RepositoryBase
from app.models import Song
from app.utils.utils_query import FilterInt


class SongRepository(RepositoryBase):
    model = Song

    def _filter_query(
        self,
        query,
        filter_artist_id_in: Optional[List[int]] = None,
        filter_out_null_genius_pageviews: bool = False,
        filter_genius_pageviews: Optional[FilterInt] = None,
        *args,
        **kwargs
    ) -> Query:
        query = self._filter_query_common(query, *args, **kwargs)

        if filter_artist_id_in is not None:
            query = query.filter(self.model.artist_id.in_(filter_artist_id_in))

        if filter_out_null_genius_pageviews:
            query = query.filter(self.model.genius_pageviews is not None)

        if filter_genius_pageviews is not None:
            query = self._apply_filter_int(
                query, self.model.genius_pageviews, filter_genius_pageviews
            )

        return query

    def _sort_query(
        self,
        query,
        # true: asc, false: desc
        order_genius_pageviews: Optional[bool] = None,
        *args,
        **kwargs
    ) -> Query:
        query = self._sort_query_common(query, *args, **kwargs)

        if order_genius_pageviews is not None:
            if order_genius_pageviews:
                order_func = asc
            else:
                order_func = desc

            query = query.order_by(order_func(self.model.genius_pageviews))

        return query
