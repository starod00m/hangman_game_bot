# - *- coding: utf- 8 - *-

from data.hangman_data import get_gallows, greetings
from random import randint
import telebot
import re
import json
from configparser import ConfigParser

# Читаем env.ini
config = ConfigParser()
config.read('env.ini')
TOKEN = config['AUTH']['TOKEN']
DICT = config['DATA']['DICT']
STATISTIC = config['DATA']['STATISTIC']

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    username = message.from_user.first_name + ' ' + message.from_user.username
    game = HangmanGame(message.from_user.id, username)
    bot.send_message(message.from_user.id, 'Начинаем игру!')
    game.greetings()
    bot.register_next_step_handler(message, game.game_runner)


@bot.message_handler(commands=['score'])
def get_stat(message):
    user_id = message.from_user.id
    stats = get_statistic(user_id)
    bot.send_message(user_id, stats)

# @bot.message_handler(commands=['full_stat'])
# def get_full_stat(message):
#     user_id = message.from_user.id
#     if user_id ==

@bot.message_handler(content_types=['text'])
def any_message(message):
    bot.send_message(message.from_user.id, 'Набери /start для начала игры')


def get_statistic(user_id):
    user_id = str(user_id)
    with open(STATISTIC, encoding='utf-8') as rf:
        statistic = json.load(rf)
        all_games = statistic[user_id]['win'] + statistic[user_id]['lose']
        wins = statistic[user_id]['win']
        loses = statistic[user_id]['lose']
    return f'Всего игр {all_games} \nИз них побед - {wins}, поражений - {loses}'


class HangmanGame:

    def __init__(self, user_id, username, attempts=10):
        self.wrong_letters = []
        self.secret_word = list(self.select_random_word().lower())
        self.known_letters = [self.secret_word[0], self.secret_word[-1]]
        self.user_id = user_id
        self.qty = attempts
        self.username = username

    @staticmethod
    def write_statistic(user_id, result, username):
        user_id = str(user_id)
        with open(STATISTIC, encoding='utf-8') as rf:
            statistic = json.load(rf)
        if user_id not in statistic:
            statistic[user_id] = {'User': username, 'win': 0, "lose": 0}
        if result == 'win':
            statistic[user_id]["win"] = statistic[user_id]["win"] + 1
        else:
            statistic[user_id]["lose"] = statistic[user_id]["lose"] + 1
        with open(STATISTIC, 'w', encoding='utf-8') as wf:
            json.dump(statistic, wf, indent=4, ensure_ascii=False)

    @staticmethod
    def select_random_word():
        with open(DICT, encoding='utf-8') as f:
            words_lst = f.readlines()
        rand_word = words_lst[randint(1, len(words_lst) - 1)].strip()
        # rand_word = words_lst[0].strip() # Берёт только первое слово, для теста
        return rand_word

    @staticmethod
    def is_endgame(word):
        if '_' in word:
            return False
        else:
            return True

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
        return f'{get_gallows(self.qty + 1)}\n{self.qty} попыток осталось\nНеправильные буквы: ' \
               f'{", ".join(self.wrong_letters)}'

    def game_runner(self, message):
        if self.add_letter_to_known(message):
            word = self.get_word()
            self.send_to_bot(word)
            if not self.is_letter_right():
                self.qty -= 1
            if self.is_endgame(word):
                self.write_statistic(self.user_id, 'win', self.username)
                self.send_to_bot(get_statistic(self.user_id))
                self.send_to_bot('Поздравляю! Ты выйграл =)\nЕсли хочешь сыграть ещё раз набери /start')
            elif self.qty == 0:
                self.send_to_bot(self.get_step_info())
                self.write_statistic(self.user_id, 'lose', self.username)
                self.send_to_bot(
                    f'Ты проиграл =(\nЗагаданное слово - {self.secret_word[0].upper() + "".join(self.secret_word[1:])}'
                    f'\nЕсли хочешь сыграть ещё раз набери /start')
                self.send_to_bot(get_statistic(self.user_id))
            else:
                self.send_to_bot(self.get_step_info())
                bot.register_next_step_handler(message, self.game_runner)
        else:
            bot.register_next_step_handler(message, self.game_runner)


if __name__ == '__main__':
    bot.polling(none_stop=True)
