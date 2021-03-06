
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
        self.config_loader = ConfigLoader()
        self.config_loader.load_config("./config.yml")
        config = self.config_loader.get_loaded_config()

        self._sensor_event_queue = queue.Queue()
        self._sensor_container = SensorContainer(config.ExtenderMapping, config.SensorMapping, self._sensor_event_queue)
        self._lane_container   = LaneContainer(config.LaneMapping)
        self._button_mapping   = config.ButtonMapping
        self._led_mapping      = config.LedMapping

        self.transition_to(state)

    def transition_to(self, state: State):
        logging.debug(f"Context: Transition to {type(state).__name__}")
        self._current_state = state
        self._current_state.context = self

        for led in self._led_mapping:
            led.turn_off()

    def start_processing(self):
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
        pause_led = self.context._led_mapping[2]
        pause_led.turn_on() # TODO: Should be run only in the constructor

        sensor_poller = self.context._sensor_container.get_sensor_poller()
        sensor_poller.stop_processing()

        # Check Transition Conditions
        start_button = self.context._button_mapping[0]
        if (start_button.is_active()):
            self.context.transition_to(RunningState())

        reset_button = self.context._button_mapping[2]
        if (reset_button.is_active()):
            self.context.transition_to(ResettingState())

class RunningState(State):
    def process(self) -> None:
        running_led = self.context._led_mapping[1]
        running_led.turn_on() # TODO: Should be run only in the constructor

        sensor_poller = self.context._sensor_container.get_sensor_poller()
        sensor_poller.start_processing()

        processor = SensorEventProcessor(self.context._sensor_event_queue, self.context._lane_container)
        scored_lane = processor.process_sensor_events()

        # Check Transition Conditions
        if (scored_lane != None):
            score_led = self.context._led_mapping[0]
            score_led.turn_on_for(100)
            if (scored_lane.reached_max_score()):
                self.context.transition_to(PausingState())

        pause_button = self.context._button_mapping[1]
        if (pause_button.is_active()):
            self.context.transition_to(PausingState())


class ResettingState(State):
    def process(self) -> None:
        reset_led = self.context._led_mapping[3]
        reset_led.turn_on() # TODO: Should be run only in the constructor

        # Check if all motors events are processed
        lane_container = self.context._lane_container
        if (lane_container.all_motor_events_processed()):
            lane_container.reset_scores_and_motors() # Set back all motors and scores

            while (not lane_container.all_motor_events_processed()):
                pass # Wait until motors are set back to start position

            self.context.transition_to(PausingState())



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


if __name__ == "__main__":
    try:
        context = GameContext(PausingState())
        context.start_processing()
    except KeyboardInterrupt:
        logging.info(f"Exiting Program!")
