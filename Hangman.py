"""Игра "Виселица\""""
from hangman_data import get_gallows, greetings
from random import randint


def select_random_word():
    with open('hangman.txt', encoding='utf-8') as f:
        words_lst = f.readlines()
    rand_word = words_lst[randint(0, len(words_lst))].strip()
    return rand_word



wrong_letters = []
secret_word = list(select_random_word().lower())
known_letters = [secret_word[0], secret_word[-1]]

def get_word():
    word_4_print = [secret_word[0].upper()]
    for letter in secret_word[1:-1]:
        if letter in known_letters:
            word_4_print.append(letter)
        else:
            word_4_print.append(' _ ')
    word_4_print.append(secret_word[-1])
    return ''.join(word_4_print)

def is_endgame(word):
    if '_' in word:
        return False
    else:
        return True

def add_letter_to_known(known_letters):
    while True:
        letter = input('Enter letter: ').lower()
        print('-------------------------\n')
        if letter not in known_letters:
            known_letters.append(letter)
            break
        else:
            print('You already entered this letter')

def is_letter_right():
    if known_letters[-1] in secret_word:
        return True
    else:
        wrong_letters.append(known_letters[-1])
        return False

def start_game(qty = 10):
    print(greetings(qty, get_word()))
    while True:
        if qty != 0:
            add_letter_to_known(known_letters)
            word = get_word()
            print(word)
            if not is_letter_right(): qty -= 1
            if is_endgame(word):
                print('Congratulation! You won =)')
                break
            print(get_gallows(qty + 1))
            print(f'{qty} attempts left')
            print(f'Wrong letters: {", ".join(wrong_letters)}\n')
        else:
            print('You lose =(')
            print(f'Word is {secret_word[0].upper() + "".join(secret_word[1:])}')
            break
