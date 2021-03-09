from sqlalchemy.orm import relationship
import enum

from app.shared.db import db
from app.shared.model import ModelBase
from app.utils import utils_date, utils_hash


class QuizStatus(enum.Enum):
    WAITING = "WAITING"
    ONGOING = "ONGOING"
    FINISHED = "FINISHED"


class Quiz(ModelBase):
    __tablename__ = "quiz"

    url = db.Column(db.String(100), unique=True, nullable=False)

    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    nbr_questions = db.Column(db.Integer, nullable=False)
    question_duration = db.Column(db.Integer, nullable=False)

    users = relationship("UserQuiz", back_populates="quiz")
    questions = relationship("QuizQuestion", back_populates="quiz")

    status = db.Column(db.Enum(QuizStatus), nullable=False)
    hidden = db.Column(db.Boolean, default=False)

    def __init__(
        self,
        name: str,
        url: str,
        nbr_questions: int,
        question_duration: int,
        description: str = None,
    ):
        self.name = name
        self.url = url
        self.nbr_questions = nbr_questions
        self.question_duration = question_duration
        self.description = description

        self.status = QuizStatus.WAITING
