from typing import List
from flask_jwt_extended import get_jwt_identity


from app.repositories import UserQuizRepository
from app.models import UserQuiz


repo_user_quiz = UserQuizRepository()


def get_history(nbr_results: int, page_nbr: int) -> List[UserQuiz]:
    current_identity = get_jwt_identity()
    return repo_user_quiz.list_(
        filter_user_id_in=[current_identity["id"]],
        filter_hidden=False,
        load_only_quiz_infos=True,
        order_creation_date=False,
        nbr_results=nbr_results,
        page_nbr=page_nbr,
        with_nbr_results=True,
    )
