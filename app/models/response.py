from sqlalchemy.orm import relationship
import enum

from app.shared.db import db
from app.shared.model import ModelBase
from app.utils import utils_date, utils_hash


class ResponseType(enum.Enum):
    ARTIST = "ARTIST"
    ALBUM = "ALBUM"
    DATE = "DATE"
    OTHER = "OTHER"


class Response(ModelBase):
    __tablename__ = "response"

    label = db.Column(db.String, nullable=False)
    type = db.Column(db.Enum(ResponseType), nullable=False)

    questions = relationship("QuestionResponse", back_populates="response")

    def __init__(self, label: str, type: ResponseType):
        self.label = label
        self.type = type
