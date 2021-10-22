
from __future__ import annotations
from abc import ABC, abstractmethod

import threading, queue

import logging
logging.basicConfig(level=logging.DEBUG)



from ConfigLoader import ConfigLoader

# TODO: Remove debug
import time

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


class GameContext:
    _current_state = None

    def __init__(self, state: State) -> None:
        logging.debug(f"{type(self).__name__}: Initializing")

        self.ConfigLoader = ConfigLoader()
        self.ConfigLoader.LoadConfig("./config.yml")

        config = self.ConfigLoader.GetLoadedConfig()
        print(config.LaneMapping)
        print(config.ExtenderMapping)
        print(config.SensorMapping)
        print(config.MotorMapping)

        exit()
        # self.NUMBER_OF_TRACKS = 2
        # self.START_SCORE      = 0
        # self.MAX_SCORE        = 25

        self._sensor_event_queue = queue.Queue()
        # self.sensor_container = SensorContainer(GLOBAL_EXTENDER_MAPPING, GLOBAL_SENSOR_MAPPING, self.sensor_event_queue)
        # self.track_container = TrackContainer(self.NUMBER_OF_TRACKS, self.START_SCORE, self.MAX_SCORE, GLOBAL_MOTOR_MAPPING)

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
