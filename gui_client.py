import sys
import wave

import pyaudio
import speech_recognition as sr
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QWidget, QPushButton, QGridLayout, QApplication, QLabel, QHBoxLayout, QVBoxLayout,
                             QMainWindow, QInputDialog)

from hangman import Hangman
from recognize import recognize_letter


class HangmanPanel(QWidget):
    def __init__(self, hangman, frames):
        super().__init__()
        self.hangman = hangman
        self.frame_index = 0
        self.frames = self.create_frames(frames)
        self.label = QLabel(self)
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.label)
        self.advance_frame()

    @staticmethod
    def create_frames(frames):
        pixel_maps = []
        for f in frames:
            pixel_maps.append(QPixmap(f))
        return pixel_maps

    def advance_frame(self):
        self.label.setPixmap(self.frames[self.frame_index])
        self.frame_index += 1

        if self.frame_index >= len(self.frames):
            self.frame_index = 0

    def reset_hangman(self):
        self.frame_index = 0
        self.advance_frame()


class MicrophonePanel(QWidget):
    def __init__(self, hangman):
        super().__init__()
        self.hangman = hangman
        self.grid = QGridLayout(self)
        self.create_button()

    def create_button(self):
        self.microphone_button = QPushButton('Recording', self)
        self.grid.addWidget(self.microphone_button, 0, 0)

    def activate_button(self):
        self.microphone_button.setEnabled(True)


class WinsPanel(QWidget):
    def __init__(self, hangman):
        super().__init__()
        self.hangman = hangman

        self.label = QLabel(self)
        self.label.setText('Wins')

        self.win_label = QLabel(self)
        self.win_label.setText('0')

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.win_label)

    def update_wins(self):
        self.win_label.setText(str(hangman.wins))


class DisplayPanel(QWidget):
    def __init__(self, hangman):
        super().__init__()
        self.hangman = hangman

        self.label = QLabel(self)
        self.word_label = QLabel(self)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.word_label)


class WordPanel(DisplayPanel):
    def __init__(self, hangman):
        super().__init__(hangman)

        self.label.setText('Current Word')
        self.update_word()

    def update_word(self):
        self.word_label.setText(' '.join(self.hangman.display_letters))


class GuessedLetterPanel(DisplayPanel):
    def __init__(self, hangman):
        super().__init__(hangman)

        self.label.setText("Letters Already Guessed")
        self.update_letters()

    def update_letters(self):
        self.word_label.setText(', '.join(self.hangman.guessed_letters))


class HangmanWindow(QMainWindow):
    def __init__(self, hangman):
        super().__init__()
        self.hangman = hangman

        self.wins_panel = WinsPanel(hangman)
        self.hangman_panel = HangmanPanel(hangman, ['hangman_0.png',
                                                    'hangman_1.png',
                                                    'hangman_2.png',
                                                    'hangman_3.png',
                                                    'hangman_4.png',
                                                    'hangman_5.png',
                                                    'hangman_6.png',
                                                    'hangman_7.png'])
        self.word_panel = WordPanel(hangman)
        self.guessed_letter_panel = GuessedLetterPanel(hangman)
        self.letter_panel = MicrophonePanel(hangman)

        central_widget = QWidget()
        central_layout = QHBoxLayout(central_widget)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(self.wins_panel)
        left_layout.addWidget(self.hangman_panel)
        left_layout.addWidget(self.word_panel)
        left_layout.addWidget(self.guessed_letter_panel)

        right_widget = QWidget()
        right_layout = QHBoxLayout(right_widget)
        right_layout.addWidget(self.letter_panel)

        central_layout.addWidget(left_widget)
        central_layout.addWidget(right_widget)

        self.connect_listeners()
        self.setCentralWidget(central_widget)
        self.setWindowTitle('Hangman')
        self.show()

    def connect_listeners(self):
        self.letter_panel.microphone_button.clicked.connect(self.on_mic_button_click)

    def on_mic_button_click(self):
        sender = self.sender()
        chunk = 1024  # Record in chunks of 1024 samples
        sample_format = pyaudio.paInt16  # 16 bits per sample
        channels = 2
        fs = 44100  # Record at 44100 samples per second
        seconds = 3
        filename = r'output.wav'

        p = pyaudio.PyAudio()  # Create an interface to PortAudio

        print('Recording')

        stream = p.open(format=sample_format,
                        channels=channels,
                        rate=fs,
                        frames_per_buffer=chunk,
                        input=True)

        frames = []  # Initialize array to store frames

        # Store data in chunks for 3 seconds
        for i in range(0, int(fs / chunk * seconds)):
            data = stream.read(chunk)
            frames.append(data)

        # Stop and close the stream 
        stream.stop_stream()
        stream.close()
        # Terminate the PortAudio interface
        p.terminate()

        print('Finished recording')

        # Save the recorded data as a WAV file
        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()

        sprec = sr.Recognizer()
        myaudiofile = sr.AudioFile('output.wav')
        with myaudiofile as source:
            myaudio = sprec.record(myaudiofile)
            rez = sprec.recognize_google(myaudio, language='ro-RO', show_all=True)
        print(rez)

        if len(rez) == 0:
            print("Could not recognize letter.")
            return
        recognized_letter = recognize_letter(rez, hangman.guessed_letters)
        if recognized_letter == "":
            print("Could not recognize letter.")
            return
        sender.setEnabled(True)

        current_guess = hangman.guesses

        self.hangman.guess_letter(recognized_letter)
        self.guessed_letter_panel.update_letters()
        self.word_panel.update_word()

        if current_guess < hangman.guesses:
            self.hangman_panel.advance_frame()

        if hangman.check_win():
            self.wins_panel.update_wins()
            self.show_win()
        elif hangman.check_lose():
            self.show_lose()

    def show_win(self):
        items = ('Yes', 'No')
        item, ok = QInputDialog.getItem(self, 'You Won!', ' Play again?', items, 0, False)
        if ok and item == 'Yes':
            self.reset_game()
        else:
            QCoreApplication.instance().quit()

    def show_lose(self):
        items = ('Yes', 'No')
        item, ok = QInputDialog.getItem(self, 'You Lost!', 'Play again?', items, 0, False)
        if ok and item == 'Yes':
            self.reset_game()
        else:
            QCoreApplication.instance().quit()

    def reset_game(self):
        hangman.start_game()
        self.wins_panel.update_wins()
        self.hangman_panel.reset_hangman()
        self.word_panel.update_word()
        self.guessed_letter_panel.update_letters()
        self.letter_panel.activate_button()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    hangman = Hangman('words.txt')
    win = HangmanWindow(hangman)
    sys.exit(app.exec_())
