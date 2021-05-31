from app.repositories import UserRepository


repo_user = UserRepository()


def list_(nbr_results: int, page_nbr: int, hidden: bool = None):
    return repo_user.list_(
        nbr_results=nbr_results,
        page_nbr=page_nbr,
        filter_hidden=hidden,
        order_creation_date=False,
        with_nbr_results=True,
    )
