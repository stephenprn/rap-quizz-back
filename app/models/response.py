from sqlalchemy.orm import relationship
import enum

from app.shared.db import db
from app.shared.model import ModelBase


class ResponseType(enum.Enum):
    ARTIST = "ARTIST"
    ALBUM = "ALBUM"
    DATE = "DATE"
    OTHER = "OTHER"
    SONG = "SONG"
    YEAR = "YEAR"

    @property
    def is_precise(self):
        return self.value == ResponseType.YEAR.value


class Response(ModelBase):
    __tablename__ = "response"

    label = db.Column(db.String, nullable=False)
    type = db.Column(db.Enum(ResponseType), nullable=False)
    hidden = db.Column(db.Boolean, nullable=False)

    questions = relationship("QuestionResponse", back_populates="response")

    __mapper_args__ = {"polymorphic_identity": "response", "polymorphic_on": type}

    def __init__(self, label: str, type: ResponseType, hidden: bool = True):
        self.label = label
        self.type = type
        self.hidden = hidden
