from hangman_data import get_gallows, greetings
from random import randint
import telebot

bot = telebot.TeleBot('1415720377:AAGyEilgj3u-Yt9yrrejCGVREasvk-Lit_0')

keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.row('/start')

@bot.message_handler(commands=['start'])
def start(message):
    game = HangmanGame(message.from_user.id)
    bot.send_message(message.from_user.id, 'Let\'s game begin!')
    game.greetings()
    bot.register_next_step_handler(message, game.game_runner)

@bot.message_handler(content_types=['text'])
def any_message(message):
    bot.send_message(message.from_user.id, 'Please type /start to start game')


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
        if letter not in self.known_letters:
            self.known_letters.append(letter)
            return True
        else:
            self.send_to_bot('You already entered this letter')
            return False

    def is_letter_right(self):
        if self.known_letters[-1] in self.secret_word:
            return True
        else:
            self.wrong_letters.append(self.known_letters[-1])
            return False

    def get_step_info(self):
        return f'''{get_gallows(self.qty + 1)}\n{self.qty} attempts left\nWrong letters: {", ".join(self.wrong_letters)}'''

    def game_runner(self, message):
        if self.add_letter_to_known(message):
            word = self.get_word()
            self.send_to_bot(word)
            if not self.is_letter_right(): self.qty -= 1
            if is_endgame(word):
                self.send_to_bot('Поздравляю! Ты выйграл =)\nЕсли хочешь сыграть ещё раз набери /start')
            elif self.qty == 0:
                self.send_to_bot(f'Ты проиграл =(\nЗагаданное слово - {self.secret_word[0].upper() + "".join(self.secret_word[1:])}'
                                 f'\nЕсли хочешь сыграть ещё раз набери /start')
            else:
                self.send_to_bot(self.get_step_info())
                bot.register_next_step_handler(message, self.game_runner)
        else:
            bot.register_next_step_handler(message, self.game_runner)


if __name__ == '__main__':
    bot.polling(none_stop=True)
