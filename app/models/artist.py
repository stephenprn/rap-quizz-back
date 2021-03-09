import json

from app.shared.db import db
from app.models import Response, ResponseType
from app.utils import utils_json

class Artist(Response):
    __tablename__ = "artist"
    __mapper_args__ = { "polymorphic_identity": ResponseType.ARTIST }

    name = db.Column(db.String(128), nullable=True)
    alternate_names = db.Column(db.JSON, nullable=True)
    description = db.Column(db.Text, nullable=True)

    fb_name = db.Column(db.String(128), nullable=True)
    instagram_name = db.Column(db.String(128), nullable=True)
    twitter_name = db.Column(db.String(128), nullable=True)

    genius_id = db.Column(db.Integer, nullable=True)
    genius_url = db.Column(db.String(128), nullable=True)
    genius_followers_count = db.Column(db.Integer, nullable=True)
    genius_header_img_url = db.Column(db.String(128), nullable=True)
    genius_profile_img_url = db.Column(db.String(128), nullable=True)
    genius_iq = db.Column(db.Integer, nullable=True)
     
    @staticmethod
    def from_dict(data: dict):
        res = Artist(data.get('name'), ResponseType.ARTIST)

        res.name = data.get('name')
        res.alternate_names = json.dumps(data.get('alternate_names'))
        res.description = utils_json.get_nested_field(data, 'description.plain')
        
        res.fb_name = data.get('facebook_name')
        res.instagram_name = data.get('instagram_name')
        res.twitter_name = data.get('twitter_name')

        res.genius_id = data.get('id')
        res.genius_url = data.get('url')
        res.genius_followers_count = data.get('followers_count')
        res.genius_header_img_url = data.get('header_image_url')
        res.genius_profile_img_url = data.get('image_url')
        res.genius_iq = data.get('iq')

        return res