from GameState import GameState

import logging
import time
import RPi.GPIO as GPIO
import pygame
import math
import numpy as np
from collections import deque
from enum import Enum


_LOGGER = logging.getLogger("MorseCodeGameEngine")


# Morse code translation dictionary and its inverse
MORSE_LETTERS = {'A': '.-', 'B': '-...', 'C': '-.-.',
                 'D': '-..',    'E': '.',      'F': '..-.',
                 'G': '--.',    'H': '....',   'I': '..',
                 'J': '.---',   'K': '-.-',    'L': '.-..',
                 'M': '--',     'N': '-.',     'O': '---',
                 'P': '.--.',   'Q': '--.-',   'R': '.-.',
                 'S': '...',    'T': '-',      'U': '..-',
                 'V': '...-',   'W': '.--',    'X': '-..-',
                 'Y': '-.--',   'Z': '--..',
               
                 '0': '-----',  '1': '.----',  '2': '..---',
                 '3': '...--',  '4': '....-',  '5': '.....',
                 '6': '-....',  '7': '--...',  '8': '---..',
                 '9': '----.'
                 }
MORSE_SYMBOLS = {symbol: letter for letter, symbol in MORSE_LETTERS.items()}

# Game modes accessible using the CMD symbol (~3 second key press)
DEFAULT_GAME_MODE = '0'
GAME_MODES = {'D': [("WHO MADE ME", "DAN"), ("AGAIN", "DAN"), ("CORRECT", "")],
              'A': [("STATE UN IDENTITY", "0012"), ("SINK", "")],
              'N': [("SINK", "")],
              'E': [("WHAT IS YOUR UBOAT NUMBER", "U110"), ("STATE UN IDENTITY NUMBER", "0012"),
                    ("UNLOCK CODE SINK HH", "")],
              '0': [("", "")]
              }

# IO pin configuration
MORSE_KEY = 24
TX_SWITCH = 23
SPEED_KEY = 4

LOW_SOUND_SAMPLES = [(2**15)*math.sin(2.0 * math.pi * 700 * t / 44100) for t in range(0, 22050)]
LOW_SOUND_SAMPLES = np.int16(LOW_SOUND_SAMPLES)
HIGH_SOUND_SAMPLES = [(2**15)*math.sin(2.0 * math.pi * 900 * t / 44100) for t in range(0, 22050)]
HIGH_SOUND_SAMPLES = np.int16(HIGH_SOUND_SAMPLES)


class MorseCodeTxRxMode(Enum):
    SEND = 0
    RECEIVE = 1


class MorseCodeGameEngine:
    mode = None

    def __init__(self, speeds=3, volumes=8):
        # Ensure we use a *copy* of the game mode's messages, otherwise they get removed permanently
        self.state = GameState(GAME_MODES[DEFAULT_GAME_MODE][:])

        self.symbol_string = ""
        self.time_since_user_acted = 0

        self.volume_steps = [volume/(volumes-1) for volume in range(volumes)]
        self.current_volume = volumes

        self.speed_steps = [0.03 + 0.02*speed/(speeds-1) for speed in range(speeds)]
        self.current_speed = 0

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(MORSE_KEY, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(TX_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(TX_SWITCH, GPIO.BOTH, callback=self.set_txrx_mode, bouncetime=200)
        GPIO.setup(SPEED_KEY, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(SPEED_KEY, GPIO.FALLING, callback=self.increase_speed, bouncetime=400)
        GPIO.setwarnings(False)
        
        # Set up sound
        pygame.mixer.init(44100, -16, 1, 1024)
        self.sound_channel = pygame.mixer.Channel(5)

        # Initialise sounds
        self.sounds = {"low_morse": pygame.mixer.Sound(LOW_SOUND_SAMPLES),
                       "high_morse": pygame.mixer.Sound(HIGH_SOUND_SAMPLES),
                       "no": pygame.mixer.Sound("no.wav"),
                       "yes": pygame.mixer.Sound("yes.wav"),
                       }

        self.key_was_up = GPIO.input(MORSE_KEY)
        self.set_txrx_mode()
        pygame.init()

        _LOGGER.debug("Game initialised")

    def increase_speed(self, *_):
        if self.current_speed < len(self.speed_steps)-1:
            self.current_speed += 1
        _LOGGER.debug("Game speed is %s", self.current_speed)

    def decrease_speed(self, *_):
        if self.current_speed > 0:
            self.current_speed -= 1
        _LOGGER.debug("Game speed is %s", self.current_speed)

    def increase_volume(self):
        if self.current_volume < len(self.volume_steps)-1:
            self.current_volume += 1
            for sound in self.sounds.values():
                sound.set_volume(self.volume_steps[self.current_volume])
        _LOGGER.debug("Sound volume is %s", self.current_volume)

    def decrease_volume(self):
        if self.current_volume > 0:
            self.current_volume -= 1
            for sound in self.sounds.values():
                sound.set_volume(self.volume_steps[self.current_volume])
        _LOGGER.debug("Sound volume is %s", self.current_volume)

    def set_txrx_mode(self, *_):
        if GPIO.input(TX_SWITCH):
            self.set_mode(MorseCodeTxRxMode.RECEIVE)
        else:
            self.set_mode(MorseCodeTxRxMode.SEND)

    def set_mode(self, mode):
        _LOGGER.debug("Switching to {}".format(mode))
        self.mode = mode

    def play_morse(self, num_steps):
        self.sounds["low_morse"].play(-1)
        for _ in range(0, num_steps):
            if self.mode == MorseCodeTxRxMode.SEND:
                break

            time.sleep(self.speed_steps[self.current_speed])
        self.sounds["low_morse"].stop()

    def play_break(self, num_steps):
        for _ in range(0, num_steps):
            if self.mode == MorseCodeTxRxMode.SEND:
                return

            time.sleep(self.speed_steps[self.current_speed])

    def play_character(self, character):
        for symbol in character:
            if self.mode == MorseCodeTxRxMode.SEND:
                return

            if symbol == ".":
                self.play_morse(4)   # dit
            elif symbol == "-":
                self.play_morse(12)  # dash
            self.play_break(8)

    def play_string(self, text_string):
        for character in text_string:
            if self.mode == MorseCodeTxRxMode.SEND:
                return

            if character in MORSE_LETTERS:
                self.play_character(MORSE_LETTERS[character])
            self.play_break(16)
        self.play_break(60)

    def run_receive_mode(self):
        self.state.reset_input()
        self.symbol_string = ""
        self.time_since_user_acted = 0
        _LOGGER.debug("Prompting the user with message: %s", self.state.challenge)
        self.play_string(self.state.challenge)

    def register_key_press(self):
        # Register a new key press by setting the state
        if self.key_was_up:
            self.sounds["high_morse"].play(loops=-1)
            self.key_was_up = False
            self.time_since_user_acted = 0

    def record_symbol(self):
        # Record the symbol
        if self.time_since_user_acted < 7:
            self.symbol_string += "."
        elif self.time_since_user_acted < 40:
            self.symbol_string += "-"
        else:
            self.symbol_string = "CMD"
            _LOGGER.debug("Command key entered, waiting for command signal")

        # Reset user input
        self.sounds["high_morse"].stop()
        self.key_was_up = True
        self.time_since_user_acted = 0

    def process_symbols(self):
        if self.time_since_user_acted == 14:
            # User has sent the command signal
            if self.symbol_string.startswith("CMD"):
                self.symbol_string = self.symbol_string[3:]

                # Valid signal received
                if self.symbol_string in MORSE_SYMBOLS and MORSE_SYMBOLS[self.symbol_string] in GAME_MODES:
                    self.sounds["yes"].play()
                    time.sleep(1.0)
                    self.sounds["yes"].stop()
                    # Ensure we use a *copy* of the game mode's messages
                    self.state.messages = GAME_MODES[MORSE_SYMBOLS[self.symbol_string]][:]
                    self.state.progress()

                # Invalid signal received
                else:
                    self.sounds["no"].play()
                    time.sleep(0.5)
                    self.sounds["no"].stop()

            # User has sent morse symbols
            elif self.symbol_string in MORSE_SYMBOLS:
                if self.state.check_input(MORSE_SYMBOLS[self.symbol_string]):
                    self.state.progress()
            self.symbol_string = ""

            # Print some debug messages to the terminal
            _LOGGER.debug("target buffer is %s", self.state.response)
            _LOGGER.debug("received buffer is %s", "".join(self.state.receivedBuffer))

    def run_send_mode(self):
        # Key is down
        if not GPIO.input(MORSE_KEY):
            self.register_key_press()
        # Key is up
        else:
            # Register a new key release by setting the state and recording the symbol
            if not self.key_was_up:
                self.record_symbol()
            # Wait for a timeout
            else:
                self.process_symbols()            

    def run_main_loop(self):
        '''Set up user input, send a status message to the command line'''
        _LOGGER.debug("target string is %s", self.state.response)
        _LOGGER.info("ready")
        while True:
            # While we're in receive mode, loop the challenge message
            if self.mode == MorseCodeTxRxMode.RECEIVE:
                self.run_receive_mode()
            # While in send mode, collect input from the user
            else:
                self.run_send_mode()
                
            # tick
            time.sleep(self.speed_steps[self.current_speed])
            self.time_since_user_acted += 1
