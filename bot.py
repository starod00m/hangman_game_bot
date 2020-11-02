# - *- coding: utf- 8 - *-

from hangman_data import get_gallows, greetings
from random import randint
import telebot
import re
import json

bot = telebot.TeleBot('1415720377:AAGyEilgj3u-Yt9yrrejCGVREasvk-Lit_0')



@bot.message_handler(commands=['start'])
def start(message):
    game = HangmanGame(message.from_user.id)
    bot.send_message(message.from_user.id, 'Начинаем игру!')
    game.greetings()
    bot.register_next_step_handler(message, game.game_runner)

@bot.message_handler(content_types=['text'])
def any_message(message):
    bot.send_message(message.from_user.id, 'Набери /start для начала игры')

def write_statistic(user_id, result):
    user_id = str(user_id)
    with open('statistic.json') as rf:
        statistic = json.load(rf)
    if user_id not in statistic:
        statistic[user_id] = {'win': 0, "lose": 0}
    if result == 'win':
        statistic[user_id]["win"] = statistic[user_id]["win"] + 1
    else:
        statistic[user_id]["lose"] = statistic[user_id]["lose"] + 1
    with open('statistic.json', 'w') as wf:
        json.dump(statistic, wf, indent=4)

def get_statistic(user_id):
    user_id = str(user_id)
    with open('statistic.json') as rf:
        statistic = json.load(rf)
        all_games = statistic[user_id]['win'] + statistic[user_id]['lose']
        wins = statistic[user_id]['win']
        loses = statistic[user_id]['lose']
    return f'''Всего игр {all_games}
Из них побед - {wins}, поражений - {loses}'''

def select_random_word():
    with open('hangman.txt', encoding='utf-8') as f:
        words_lst = f.readlines()
    rand_word = words_lst[randint(0, len(words_lst) - 1)].strip()
    return rand_word

def is_endgame(word):
    if '_' in word:
        return False
    else:
        return True

class HangmanGame:

    def __init__(self, user_id, qty = 10):
        self.wrong_letters = []
        self.secret_word = list(select_random_word().lower())
        self.known_letters = [self.secret_word[0], self.secret_word[-1]]
        self.user_id = user_id
        self.qty = qty

    def greetings(self):
        self.send_to_bot(greetings(self.qty, self.get_word()))

    def send_to_bot(self, message):
        bot.send_message(self.user_id, message)

    def get_word(self):
        word_4_print = [self.secret_word[0].upper()]
        for letter in self.secret_word[1:-1]:
            if letter in self.known_letters:
                word_4_print.append(letter)
            else:
                word_4_print.append(' _ ')
        word_4_print.append(self.secret_word[-1])
        return ''.join(word_4_print)

    def add_letter_to_known(self, message):
        letter = message.text.lower()
        if len(letter) > 1:
            self.send_to_bot('Вводи буквы по одной')
            return False
        elif not re.match(r'[а-я]', letter):
            self.send_to_bot('Только русские буквы, пожалуйста')
        elif letter in self.known_letters:
            self.send_to_bot('Ты уже вводил эту букву')
            return False
        else:
            self.known_letters.append(letter)
            return True

    def is_letter_right(self):
        if self.known_letters[-1] in self.secret_word:
            return True
        else:
            self.wrong_letters.append(self.known_letters[-1])
            return False

    def get_step_info(self):
        return f'''{get_gallows(self.qty + 1)}\n{self.qty} попыток осталось\nНеправильные буквы: {", ".join(self.wrong_letters)}'''

    def game_runner(self, message):
        if self.add_letter_to_known(message):
            word = self.get_word()
            self.send_to_bot(word)
            if not self.is_letter_right(): self.qty -= 1
            if is_endgame(word):
                write_statistic(self.user_id, 'win')
                self.send_to_bot(get_statistic(self.user_id))
                self.send_to_bot('Поздравляю! Ты выйграл =)\nЕсли хочешь сыграть ещё раз набери /start')
            elif self.qty == 0:
                self.send_to_bot(self.get_step_info())
                write_statistic(self.user_id, 'lose')
                self.send_to_bot(f'Ты проиграл =(\nЗагаданное слово - {self.secret_word[0].upper() + "".join(self.secret_word[1:])}'
                                 f'\nЕсли хочешь сыграть ещё раз набери /start')
                self.send_to_bot(get_statistic(self.user_id))
            else:
                self.send_to_bot(self.get_step_info())
                bot.register_next_step_handler(message, self.game_runner)
        else:
            bot.register_next_step_handler(message, self.game_runner)


if __name__ == '__main__':
    bot.polling(none_stop=True)
