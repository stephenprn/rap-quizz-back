import enum


class QuizPlayerAnswerStatus(enum.Enum):
    RIGHT = "RIGHT"
    WRONG = "WRONG"
    NONE = "NONE"


class QuizPlayer:
    def __init__(self, uuid: str, username: str, admin: bool = False):
        self.uuid = uuid
        self.username = username
        self.answer_status = QuizPlayerAnswerStatus.NONE
        self.admin = admin
        self.score = 0
