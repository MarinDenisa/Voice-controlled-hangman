from random import randint


class Hangman:
    def __init__(self, word_list_file, allowed_guesses=6):
        self.words = self.read_word_file(word_list_file)
        self.allowed_guesses = allowed_guesses
        self.start_game()
        self.wins = 0

    def start_game(self):
        self.secret_word = self.pick_secret_word()
        self.display_letters = self.create_display_letters()
        self.guessed_letters = []
        self.guesses = 0

    @staticmethod
    def read_word_file(word_list_file):
        word_list = []
        with open(word_list_file, 'r') as f:
            for line in f:
                word_list.append(line.rstrip())
        return word_list

    def pick_secret_word(self):
        index = randint(0, len(self.words) - 1)
        return self.words[index].upper()

    def create_display_letters(self):
        letters = []
        for _ in self.secret_word:
            letters.append('-')
        return letters

    def guess_letter(self, letter):
        if letter not in self.guessed_letters:
            guess_wrong = True
            self.guessed_letters.append(letter)
            for i in range(len(self.secret_word)):
                if letter == self.secret_word[i]:
                    guess_wrong = False
                    self.display_letters[i] = letter
            if guess_wrong:
                self.guesses += 1

    def check_win(self):
        word = ''.join(self.display_letters)
        if word == self.secret_word and self.guesses <= self.allowed_guesses:
            self.wins += 1
            return True
        else:
            return False

    def check_lose(self):
        return self.guesses > self.allowed_guesses
