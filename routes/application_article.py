from flask import Blueprint, request, Response
from flask_jwt import jwt_required

from services import service_article
from shared.annotations import pagination

application_article = Blueprint("application_article", __name__)


@application_article.route("/")
def hello():
    return "hello admin"


@application_article.route("/articles-list")
@pagination(20)
def get_articles_list(nbr_results: int, page_nbr: int):
    return service_article.get_articles_list(nbr_results, page_nbr)


@application_article.route("/article-details/<art_url>")
def get_article(art_url: str):
    return service_article.get_article(art_url)


@application_article.route("/add-article", methods=["POST"])
@jwt_required()
def add_article():
    title = request.form.get("title")
    body = request.form.get("body")

    service_article.add_article(title, body=body)

    return Response(status = 204)