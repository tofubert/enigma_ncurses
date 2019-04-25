#!/usr/bin/env python
from morse.game_engine import MorseCodeGameEngine

import logging

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger("MorseGameMain")
_LOGGER.disabled = True


# If we've been explicitly called then start the default game
if __name__ == '__main__':
    _LOGGER.disabled = False
    engine = MorseCodeGameEngine()
    engine.set_volume(7)
    engine.run()
