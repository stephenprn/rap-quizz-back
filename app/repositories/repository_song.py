from typing import Optional, List
from sqlalchemy import desc

from app.shared.repository import RepositoryBase

from app.models import Song


class SongRepository(RepositoryBase):
    model = Song

    def get_top_by_artist_id(self, artist_id: int,
                             nbr_results: Optional[int] = 5,
                             page: Optional[int] = 0) -> List[Song]:
        query = self.model.query.filter(
            self.model.artist_id == artist_id,
            self.model.genius_pageviews != None
        ).order_by(desc(self.model.genius_pageviews))

        query = self._paginate(query, nbr_results=nbr_results, page_nbr=page)

        return query.all()
