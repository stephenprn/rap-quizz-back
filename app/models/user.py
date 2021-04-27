from sqlalchemy.orm import relationship
import enum

from app.shared.db import db
from app.utils import utils_hash
from app.shared.model import ModelBase


class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class User(ModelBase):
    __tablename__ = "users"

    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    color = db.Column(db.String(128), nullable=False)

    password = db.Column(db.String(128), nullable=False)
    salt = db.Column(db.String(128), nullable=False)

    quizzes = relationship("UserQuiz", back_populates="user")
    questions_created = relationship(
        "Question", back_populates="author", cascade="all, delete-orphan"
    )

    questions = relationship("UserQuestion", back_populates="user")

    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        role: UserRole = UserRole.USER,
        color: str = "#ffffff",
    ):
        self.username = username
        self.email = email
        self.role = role
        self.color = color

        pw_salt = utils_hash.hash_password(password)

        self.password = pw_salt[0]
        self.salt = pw_salt[1]
