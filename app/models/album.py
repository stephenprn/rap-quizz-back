
from app.shared.db import db
from app.models import Response, ResponseType
from app.utils import utils_json


class Album(Response):
    __tablename__ = "album"
    __mapper_args__ = {"polymorphic_identity": ResponseType.ALBUM}

    id = db.Column(
        db.Integer,
        db.ForeignKey("response.id", onupdate="cascade", ondelete="cascade"),
        primary_key=True,
    )

    title = db.Column(db.String(128), nullable=True)
    title_with_featured = db.Column(db.String(128), nullable=True)

    genius_annotations_count = db.Column(db.Integer, nullable=True)
    genius_header_img_url = db.Column(db.String(128), nullable=True)
    genius_cover_img_url = db.Column(db.String(128), nullable=True)
    genius_pyongs_count = db.Column(db.Integer, nullable=True)
    genius_hot = db.Column(db.Boolean, nullable=True)
    genius_pageviews = db.Column(db.Integer, nullable=True)

    def __init__(self, label: str):
        super().__init__(label, ResponseType.ALBUM)
        self.title = label

    @staticmethod
    def from_dict(data: dict) -> "Album":
        res = Album(data.get("title"))

        res.title = data.get("title")
        res.title_with_featured = data.get("title_with_featured")

        res.genius_id = data.get("id")
        res.genius_annotations_count = data.get("annotation_count")
        res.genius_header_img_url = data.get("header_image_url")
        res.genius_cover_img_url = data.get("song_art_image_url")
        res.genius_url = data.get("url")
        res.genius_pyongs_count = data.get("pyongs_count")
        res.genius_hot = utils_json.get_nested_field(data, "stats.hot")
        res.genius_pageviews = utils_json.get_nested_field(data, "stats.pageviews")

        return res
