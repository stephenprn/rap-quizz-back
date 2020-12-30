from typing import List

from . import QuizPlayer, QuizPlayerAnswerStatus
from app.models import QuizQuestion
from app.services import service_quiz

class QuizRoom:
    def __init__(self, name: str):
        self.name = name
        self.index = 0

        self.questions = []
        self.players = []

    def increment_index(self):
        self.index += 1
        return self.index

    def add_player(self, player: QuizPlayer):
        self.players.append(player)
        return self.players

    def remove_player(self, player_uuid: str):
        self.players = [p for p in self.players if p.uuid != player_uuid]
        return self.players

    def add_questions(self, quiz_questions: List[QuizQuestion]):
        for quiz_question in quiz_questions:
            question_dict, correct_response = service_quiz.generate_question_dict(
            quiz_question.question, quiz_question.responses_false)

            self.questions.append({
                'question_dict': question_dict,
                'correct_response': correct_response.response.uuid
            })

    def get_question(self, index: int = None):
        if index == None:
            index = self.index

        if index >= len(self.questions):
            return None

        return self.questions[index]['question_dict']

    def player_answer(self, player_uuid: str, question_uuid: str, response_uuid: str):
        player = self.__get_player(player_uuid)

        if player == None:
            raise ValueError('Player not found in this quiz')

        if player.answer_status != QuizPlayerAnswerStatus.NONE:
            raise TypeError('Player already answered')

        answer_correct = self.__check_right_response(question_uuid, response_uuid)

        if answer_correct:
            player.answer_status = QuizPlayerAnswerStatus.RIGHT
        else:
            player.answer_status = QuizPlayerAnswerStatus.WRONG
        
        return answer_correct

    def all_players_answered(self):
        return all(player.answer_status != QuizPlayerAnswerStatus.NONE for player in self.players)

    def reset_all_players_answer_status(self):
        for player in self.players:
            player.answer_status = QuizPlayerAnswerStatus.NONE


    def __get_player(self, player_uuid: str):
        return next((player for player in self.players if player.uuid == player_uuid), None)

    def __check_right_response(self, question_uuid: str, response_uuid: str):
        question = next(q for q in self.questions if q["question_dict"]["uuid"] == question_uuid)

        if question == None:
            raise ValueError('Question not found in this quiz')
            
        return question['correct_response'] == response_uuid
