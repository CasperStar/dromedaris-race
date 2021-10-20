
from __future__ import annotations
from abc import ABC, abstractmethod

import logging
logging.basicConfig(level=logging.DEBUG)

from ConfigParser import ConfigParser

# TODO: Remove debug
import time

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


class GameContext:
    _current_state = None

    def __init__(self, state: State) -> None:
        logging.debug(f"{type(self).__name__}: Initializing")

        self.ConfigLoader = ConfigParser()
        self.ConfigLoader.LoadConfig2("./config.yml")

        self.transition_to(state)

    def transition_to(self, state: State):
        logging.debug(f"Context: Transition to {type(state).__name__}")
        self._current_state = state
        self._current_state.context = self

    def StartProcessing(self):
        logging.debug(f"{type(self).__name__}: Start processing")
        while(1):
            self._current_state.process()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


class State(ABC):
    @property
    def context(self) -> GameContext:
        return self._context

    @context.setter
    def context(self, context: GameContext) -> None:
        self._context = context

    @abstractmethod
    def process(self) -> None:
        pass

class PausingState(State):
    def process(self) -> None:
        logging.debug(f"Start Processing {type(self).__name__}")
        logging.debug(f"Start tranision to next state!")
        time.sleep(3)
        self.context.transition_to(RunningState())

class RunningState(State):
    def process(self) -> None:
        logging.debug(f"Start Processing {type(self).__name__}")
        logging.debug(f"Start tranision to next state!")
        time.sleep(3)
        self.context.transition_to(ResettingState())

class ResettingState(State):
    def process(self) -> None:
        logging.debug(f"Start Processing {type(self).__name__}")
        logging.debug(f"Start tranision to next state!")
        time.sleep(3)
        self.context.transition_to(PausingState())


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


if __name__ == "__main__":
    try:
        context = GameContext(PausingState())
        context.StartProcessing()
    except KeyboardInterrupt:
        logging.info(f"Exiting Program!")