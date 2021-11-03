
from __future__ import annotations
from abc import ABC, abstractmethod

import threading, queue

import logging

logging.basicConfig(level=logging.DEBUG)

from ConfigLoader import ConfigLoader

# TODO: Remove debug
import time


from Sensor import SensorContainer, SensorEventProcessor
from Lane import LaneContainer
from MotorControl import MotorController

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


class GameContext:
    _current_state = None

    def __init__(self, state: State) -> None:
        logging.debug(f"{type(self).__name__}: Initializing")

        # Read + Load Configuration 
        self.ConfigLoader = ConfigLoader()
        self.ConfigLoader.LoadConfig("./config.yml")
        config = self.ConfigLoader.GetLoadedConfig()

        self._sensor_event_queue = queue.Queue()
        self._sensor_container = SensorContainer(config.ExtenderMapping, config.SensorMapping, self._sensor_event_queue)
        self._motor_controller = MotorController(0x04)
        self._lane_container   = LaneContainer(config.LaneMapping, config.MotorMapping) # TODO: Motor and Lane still need to get coupeled

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

    def __init__(self):
        logging.info(f"Initializing State Machine State: {type(self).__name__}")

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
        sensor_poller = self.context._sensor_container.get_sensor_poller()
        sensor_poller.stop()

        time.sleep(3)
        self.context.transition_to(RunningState())

class RunningState(State):
    def process(self) -> None:
        sensor_poller = self.context._sensor_container.get_sensor_poller()
        sensor_poller.start() # TODO: This should be moved to the init of the class instead of the processing function. Have some problems with the inheritance

        processor = SensorEventProcessor(self.context._sensor_event_queue, self.context._lane_container)
        scored_lane = processor.process_sensor_events() 

        if (scored_lane != None):
            if (scored_lane.reached_max_score()):
                self.context.transition_to(PausingState())

class ResettingState(State):
    def process(self) -> None:
        logging.debug(f"Start Processing {type(self).__name__}")
#        time.sleep(1)
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
