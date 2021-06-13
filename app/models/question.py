import enum

from sqlalchemy.orm import relationship

from .response import ResponseType
from app.shared.db import db
from app.shared.model import ModelBase


class QuestionSubType(enum.Enum):
    HIT = "HIT"
    ARTIST_PICTURE = "ARTIST_PICTURE"
    RANKING = "RANKING"
    UNKNOWN = "UNKNOWN"
    LYRICS = "LYRICS"


class Question(ModelBase):
    __tablename__ = "question"

    label = db.Column(db.String, nullable=False)
    type = db.Column(db.Enum(ResponseType), nullable=False)
    picture = db.Column(db.String, nullable=True)
    sub_type = db.Column(db.Enum(QuestionSubType), nullable=False)
    explaination = db.Column(db.Text, nullable=True)

    hidden = db.Column(db.Boolean, nullable=False)

    users = relationship("UserQuestion", back_populates="question")
    quizzes = relationship("QuizQuestion", back_populates="question")
    responses = relationship(
        "QuestionResponse",
        back_populates="question",
        cascade="save-update, merge, delete, delete-orphan",
    )
    response_precise = db.Column(db.String, nullable=True)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="questions_created")

    def __init__(self, label: str, hidden: bool = False):
        self.label = label
        self.hidden = hidden
