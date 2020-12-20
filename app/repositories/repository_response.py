from typing import Optional

from app.shared.repository import RepositoryBase

from app.models import Response, ResponseType


class ResponseRepository(RepositoryBase):
    model = Response

    def list_from_search_txt(
        self,
        search_txt: str,
        type: ResponseType,
        nbr_results: Optional[int] = None,
        page: Optional[int] = None,
    ):
        query = self.model.query.filter(
            self.model.label.ilike(f"%{search_txt}%"), self.model.type == type
        )

        query = self._paginate(query, nbr_results=nbr_results, page=page)

        return query.all()

    def get_by_uuid(self, uuid: str):
        return self.model.query.filter(self.model.uuid == uuid).scalar()

    def get(self, label: str, type: ResponseType):
        return self.model.query.filter(
            self.model.label == label, self.model.type == type
        ).scalar()
