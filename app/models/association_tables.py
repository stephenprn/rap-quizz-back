from sqlalchemy import Table
from sqlalchemy.orm import relationship
import enum

from app.shared.db import db
from app.shared.model import ModelAssociation


class UserQuizStatus(enum.Enum):
    ADMIN = "ADMIN"
    PLAYER = "PLAYER"


class UserQuiz(ModelAssociation):
    __tablename__ = "user_quiz"

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), primary_key=True)

    user = relationship("User", back_populates="quizzes")
    quiz = relationship("Quiz", back_populates="users")

    status = db.Column(db.Enum(UserQuizStatus))
    score = db.Column(db.Integer)

    creation_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, user_id: int, quiz_id: int, status: UserQuizStatus = None):
        self.user_id = user_id
        self.quiz_id = quiz_id

        self.status = status


# status on how the user answered the question


class UserQuestionStatus(enum.Enum):
    CORRECT = "CORRECT"
    WRONG = "WRONG"


class UserQuestion(ModelAssociation):
    __tablename__ = "user_question"

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), primary_key=True)

    user = relationship("User", back_populates="questions")
    question = relationship("Question", back_populates="users")

    status = db.Column(db.Enum(UserQuestionStatus), nullable=False)


class QuizQuestion(ModelAssociation):
    __tablename__ = "quiz_question"
    id = db.Column(db.Integer, unique=True)

    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), primary_key=True)

    quiz = relationship("Quiz", back_populates="questions")
    question = relationship("Question", back_populates="quizzes")
    question_index = db.Column(db.Integer)
    responses_false = relationship(
        "QuizQuestionResponse", back_populates="quiz_question"
    )

    def __init__(self, quiz_id: int, question_id: int, question_index: int):
        self.quiz_id = quiz_id
        self.question_id = question_id
        self.question_index = question_index

        self.id = int(str(quiz_id) + str(question_id))


class QuizQuestionResponse(ModelAssociation):
    __tablename__ = "quiz_question_response"

    quiz_question_id = db.Column(
        db.Integer, db.ForeignKey("quiz_question.id"), primary_key=True
    )
    response_id = db.Column(db.Integer, db.ForeignKey("response.id"), primary_key=True)

    quiz_question = relationship("QuizQuestion", back_populates="responses_false")
    response = relationship("Response")

    def __init__(self, quiz_question_id: int, response_id: int):
        self.quiz_question_id = quiz_question_id
        self.response_id = response_id


# status on is the response is the right one or not


class QuestionResponseStatus(enum.Enum):
    CORRECT = "CORRECT"
    WRONG = "WRONG"


class QuestionResponse(ModelAssociation):
    __tablename__ = "question_response"

    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey("response.id"), primary_key=True)

    question = relationship("Question", back_populates="responses")
    response = relationship("Response", back_populates="questions")

    status = db.Column(db.Enum(QuestionResponseStatus), nullable=False)

    def __init__(
        self,
        question_id: int,
        response_id: int,
        status: QuestionResponseStatus = QuestionResponseStatus.CORRECT,
    ):
        self.question_id = question_id
        self.response_id = response_id

        self.status = status
