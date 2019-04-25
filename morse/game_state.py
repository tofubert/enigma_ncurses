import editdistance
import logging
from collections import deque

_LOGGER = logging.getLogger("GameState")


class GameState:
    """
    Game state variable containing the messages and methods to check input
    """
    # Variable defaults
    challenge = None
    response = None
    receivedBuffer = None

    # Constructor
    def __init__(self, messages):
        self.messages = messages
        self.progress()

    # Check if the user's input is correct
    def check_input(self, symbol):
        _LOGGER.debug("Appending {} and checking against target".format(symbol))
        self.receivedBuffer.append(symbol)
        return self.response != "" and editdistance.eval("".join(self.receivedBuffer), self.response) < 2

    # Progress to the next message
    def progress(self):
        _LOGGER.info("Incrementing game level")
        self.challenge, self.response = self.messages.pop(0)
        self.reset_input()
    
    # Reset the input buffer
    def reset_input(self):
        self.receivedBuffer = deque("_"*len(self.response), maxlen=len(self.response))

    # Return a string showing the game state (used by print())
    def __str__(self):
        if self.challenge and self.response:
            return "Game in progress - target messages:\n  {0}\n  {1}".format(
                    self.challenge + " -> " + self.response,
                    "\n  ".join([c + " -> " + r for c, r in self.messages])
                )
        elif self.challenge:
            return "Game has ended - final message:\n  {0}".format(
                    self.challenge + " -> " + self.response
                )
        else:
            return "No game in progress"

    # Return a string which could reproduce this object if evaluated
    def __repr__(self):
        return "GameState({0})".format([(self.challenge, self.response)] + self.messages)
