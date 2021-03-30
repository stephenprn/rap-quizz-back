from app.shared.repository import RepositoryBase

from app.models import Artist


class ArtistRepository(RepositoryBase):
    model = Artist

    def get_by_genius_id(self, genius_id: int) -> Artist:
        return self.model.query.filter(self.model.genius_id == genius_id).scalar()
