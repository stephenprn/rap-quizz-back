from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship


from app.shared.db import db
from app.models import Response, ResponseType, Response
from app.models.artist import Artist
from app.utils import utils_json


class Song(Response):
    __tablename__ = "song"
    __mapper_args__ = {"polymorphic_identity": ResponseType.SONG}

    id = db.Column(
        db.Integer,
        db.ForeignKey("response.id", onupdate="cascade", ondelete="cascade"),
        primary_key=True,
    )

    title = db.Column(db.String(128), nullable=True)
    title_full = db.Column(db.String(128), nullable=True)
    title_with_featured = db.Column(db.String(128), nullable=True)

    genius_annotations_count = db.Column(db.Integer, nullable=True)
    genius_cover_img_url = db.Column(db.String(128), nullable=True)
    genius_pyongs_count = db.Column(db.Integer, nullable=True)
    genius_hot = db.Column(db.Boolean, nullable=True)
    genius_pageviews = db.Column(db.Integer, nullable=True)

    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"))
    artist = relationship(
        Artist,
        back_populates="songs",
        foreign_keys=[artist_id])

    def __init__(self, label: str):
        super().__init__(label, ResponseType.SONG)
        self.title = label

    @declared_attr
    def genius_id(cls):
        return Response.__table__.c.get(
            "genius_id", db.Column(db.Integer, nullable=True)
        )

    @declared_attr
    def genius_url(cls):
        return Response.__table__.c.get(
            "genius_url", db.Column(db.String(128), nullable=True)
        )

    @declared_attr
    def genius_header_img_url(cls):
        return Response.__table__.c.get(
            "genius_header_img_url", db.Column(db.String(128), nullable=True)
        )

    @staticmethod
    def from_dict(data: dict, artist: Artist):
        res = Song(data.get("title"))

        res.title = data.get("title")[:128]
        res.title_full = data.get("full_title")[:128]
        res.title_with_featured = data.get("title_with_featured")[:128]

        res.genius_id = data.get("id")
        res.genius_annotations_count = data.get("annotation_count")
        res.genius_header_img_url = data.get("header_image_url")
        res.genius_cover_img_url = data.get("song_art_image_url")[:128]
        res.genius_url = data.get("url")
        res.genius_pyongs_count = data.get("pyongs_count")
        res.genius_hot = utils_json.get_nested_field(data, "stats.hot")
        res.genius_pageviews = utils_json.get_nested_field(
            data, "stats.pageviews")

        res.artist_id = artist.id

        return res
