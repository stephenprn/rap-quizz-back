from sqlalchemy.orm import relationship

from app.shared.db import db
from app.shared.model import ModelBase
from app.utils import utils_date, utils_hash


class Quiz(ModelBase):
    __tablename__ = "quiz"

    url = db.Column(db.String(100), unique=True, nullable=False)

    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    nbr_questions = db.Column(db.Integer, nullable=False)

    users = relationship("UserQuiz", back_populates="quiz")
    questions = relationship("QuizQuestion", back_populates="quiz")

    hidden = db.Column(db.Boolean, default=False)

    def __init__(
        self, name: str, url: str, nbr_questions: int, description: str = None
    ):
        self.name = name
        self.url = url
        self.nbr_questions = nbr_questions
        self.description = description
