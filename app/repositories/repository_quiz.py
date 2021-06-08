from typing import List, Optional

from sqlalchemy.orm import joinedload

from app.shared.repository import RepositoryBase

from app.models import Quiz, UserQuiz


class QuizRepository(RepositoryBase):
    model = Quiz

    def _filter_query(
        self, query, filter_url_in: Optional[List[str]] = None, *args, **kwargs
    ):
        query = self._filter_query_common(query, *args, **kwargs)

        if filter_url_in is not None:
            query = query.filter(self.model.url.in_(filter_url_in))

        return query

    def _load_only(
        self, query, load_only_users: Optional[bool] = False, *args, **kwargs
    ):
        if load_only_users:
            query = query.join(
                self.model.users).options(
                joinedload(
                    self.model.users) .load_only(
                    "status",
                    "creation_date") .options(
                    joinedload(
                        UserQuiz.user).load_only(
                            "username",
                            "uuid",
                        "color")))

        return query
