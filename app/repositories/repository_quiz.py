from sqlalchemy.orm import joinedload

from app.shared.repository import RepositoryBase

from app.models import Quiz


class QuizRepository(RepositoryBase):
    model = Quiz

    def get_one_by_url(self, url: str):
        return (
            self.model.query.filter(url == url)
            .options(joinedload(self.model.questions))
            .first()
        )
