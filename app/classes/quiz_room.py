from typing import List, Optional

from . import QuizPlayer, QuizPlayerAnswerStatus
from app.models import QuizQuestion, QuizStatus, Quiz
from app.services import service_quiz


class QuizRoom:
    def __init__(self, quiz: Quiz,  admin_uuid: str):
        self.name = quiz.name
        self.url = quiz.url
        self.nbr_questions = quiz.nbr_questions
        self.question_duration = quiz.question_duration
        self.description = quiz.description

        self.admin_uuid = admin_uuid
        self.index = 0
        self.status = QuizStatus.WAITING

        self.questions = []
        self.players = []

        self.question_scheduler = None
        self.question_scheduler_event = None

    def __repr__(self):
        return f"<QuizRoom name={self.name} admin_uuid={self.admin_uuid} status={self.status}>"

    def increment_index(self) -> int:
        self.index += 1
        return self.index

    def add_player(self, player: QuizPlayer) -> List[QuizPlayer]:
        self.players.append(player)
        return self.players

    def remove_player(self, player_uuid: str) -> List[QuizPlayer]:
        self.players = [p for p in self.players if p.uuid != player_uuid]
        return self.players

    def set_status(self, status: QuizStatus) -> None:
        self.status = status

    def add_questions(self, quiz_questions: List[QuizQuestion]) -> List[dict]:
        for index, quiz_question in enumerate(quiz_questions):
            question_dict, correct_response = service_quiz.generate_question_dict(
                quiz_question.question, quiz_question.responses_false)
            question_dict["index"] = index + 1

            self.questions.append({
                'question_dict': question_dict,
                'correct_response': correct_response.response.uuid
            })

        return self.questions

    def get_question(self, index: int = None) -> Optional[dict]:
        if index == None:
            index = self.index

        if index >= len(self.questions):
            return None

        return self.questions[index]['question_dict']

    def player_answer(self, player_uuid: str, question_uuid: str, response_uuid: str) -> bool:
        player = self.get_player(player_uuid)

        if player == None:
            raise ValueError('Player not found in this quiz')

        if player.answer_status != QuizPlayerAnswerStatus.NONE:
            raise TypeError('Player already answered')

        answer_correct = self.__check_right_response(
            question_uuid, response_uuid)

        if answer_correct:
            player.answer_status = QuizPlayerAnswerStatus.RIGHT
            player.score += 1
        else:
            player.answer_status = QuizPlayerAnswerStatus.WRONG

        return answer_correct

    def all_players_answered(self) -> bool:
        return all(player.answer_status != QuizPlayerAnswerStatus.NONE for player in self.players)

    def reset_all_players_answer_status(self) -> None:
        for player in self.players:
            player.answer_status = QuizPlayerAnswerStatus.NONE

    def set_admin_if_not_exists(self) -> Optional[QuizPlayer]:
        if len(self.players) == 0 or next((player for player in self.players if player.admin), None) != None:
            return None

        new_admin = self.players[0]
        new_admin.admin = True

        return new_admin

    def is_admin(self, player_uuid: str) -> bool:
        return self.get_player(player_uuid).admin

    def set_question_scheduler(self, question_scheduler, question_scheduler_event: str):
        self.question_scheduler = question_scheduler
        self.question_scheduler_event = question_scheduler_event

    def cancel_question_scheduler(self):
        self.question_scheduler.cancel(self.question_scheduler_event)

        self.question_scheduler = None
        self.question_scheduler_event = None

    def get_player(self, player_uuid: str) -> Optional[QuizPlayer]:
        return next((player for player in self.players if player.uuid == player_uuid), None)

    def __check_right_response(self, question_uuid: str, response_uuid: str) -> bool:
        question = next(
            q for q in self.questions if q["question_dict"]["uuid"] == question_uuid)

        if question == None:
            raise ValueError('Question not found in this quiz')

        return question['correct_response'] == response_uuid
