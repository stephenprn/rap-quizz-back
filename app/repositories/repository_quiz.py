from sqlalchemy.orm import joinedload

from app.shared.repository import RepositoryBase

from app.models import Quiz, UserQuiz


class QuizRepository(RepositoryBase):
    model = Quiz

    def get_one_by_url(self, url: str, with_users: bool = False):
        query = self.model.query.filter(self.model.url == url)

        if with_users:
            query = query.join(self.model.users).options(
                joinedload(self.model.users)
                .load_only("status", "creation_date")
                .options(joinedload(UserQuiz.user).load_only("username", "uuid"))
            )
        
        return query.first()

    
