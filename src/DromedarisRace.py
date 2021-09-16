import logging, sys
import threading, queue
import time
import RPi.GPIO as GPIO

from Sensor import MicroSwitch, SensorContainer, EdgeEventEnum
from IOControl import MCP23017, RaspberryPinPWM, ExtenderPin, IODirection
from Motor import DCMotor
from ThrowingTrack import TrackContainer


# Setup Logging Parameters
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

GLOBAL_EXTENDER_MAPPING = ( MCP23017(0x20, 0b00111111, 0b11111111, 0b00111111, 0b11111111),) # Track 1 - Track 4
                            #MCP23017(0x21, 0b00111111, 0b11111111, 0b00000111, 0b11111111), # Track 5 - Track 6
                            #MCP23017(0x22, 0b00000000, 0b11111111, 0b00000000, 0b11111111)) # Motor 1 - Motor 6

GLOBAL_SENSOR_MAPPING = ( MicroSwitch(0, 1, 0x20,  0, 500), MicroSwitch(0, 2, 0x20,  1, 500), MicroSwitch(0, 3, 0x20,  2, 500), # Track 1
                          MicroSwitch(1, 1, 0x20,  3, 500), MicroSwitch(1, 2, 0x20,  4, 500), MicroSwitch(1, 3, 0x20,  5, 500)) # Track 2
                         #MicroSwitch(2, 1, 0x20,  8, 500), MicroSwitch(2, 2, 0x20,  9, 500), MicroSwitch(2, 3, 0x20, 10, 500), # Track 3
                         #MicroSwitch(3, 1, 0x20, 11, 500), MicroSwitch(3, 2, 0x20, 12, 500), MicroSwitch(3, 3, 0x20, 13, 500), # Track 4
                         #MicroSwitch(4, 1, 0x21,  0, 500), MicroSwitch(4, 2, 0x21, 01, 500), MicroSwitch(4, 3, 0x21,  2, 500), # Track 5
                         #MicroSwitch(5, 1, 0x21,  3, 500), MicroSwitch(5, 2, 0x21, 04, 500), MicroSwitch(5, 3, 0x21,  5, 500), # Track 6

GLOBAL_MOTOR_MAPPING = ( DCMotor(0, RaspberryPinPWM( 8, 100), ExtenderPin(0x20,   6, IODirection.OUTPUT), ExtenderPin(0x20,   7, IODirection.OUTPUT)), # Track 1
                         DCMotor(1, RaspberryPinPWM(10, 100), ExtenderPin(0x20,  14, IODirection.OUTPUT), ExtenderPin(0x20,  15, IODirection.OUTPUT))) # Track 2
                         #DCMotor(2, RaspberryPinPWM(12, 100), ExtenderPin(0x22,  4, IODirection.OUTPUT), ExtenderPin(0x22,  5, IODirection.OUTPUT)), # Track 3
                         #DCMotor(3, RaspberryPinPWM(16, 100), ExtenderPin(0x22,  6, IODirection.OUTPUT), ExtenderPin(0x22,  7, IODirection.OUTPUT)), # Track 4
                         #DCMotor(4, RaspberryPinPWM(18, 100), ExtenderPin(0x22,  8, IODirection.OUTPUT), ExtenderPin(0x22,  9, IODirection.OUTPUT)), # Track 5
                         #DCMotor(5, RaspberryPinPWM(22, 100), ExtenderPin(0x22, 10, IODirection.OUTPUT), ExtenderPin(0x22, 11, IODirection.OUTPUT))) # Track DirectCurrentMotor

# Setup Main Class
class DromedarisRace:
    def __init__(self) -> None:
        logging.debug("DromedarisRace: Initializing")

        self.NUMBER_OF_TRACKS = 2
        self.START_SCORE      = 0
        self.MAX_SCORE        = 25

        self.sensor_event_queue = queue.Queue()
        self.sensor_container = SensorContainer(GLOBAL_EXTENDER_MAPPING, GLOBAL_SENSOR_MAPPING, self.sensor_event_queue)
        self.track_container = TrackContainer(self.NUMBER_OF_TRACKS, self.START_SCORE, self.MAX_SCORE, GLOBAL_MOTOR_MAPPING)

    def __process_sensor_events(self):
        sensor_event = self.sensor_event_queue.get()

        if (EdgeEventEnum.EDGE_DETECT_FALLING == sensor_event.get_edge_event()):
            track = self.track_container.get_track(sensor_event.get_track_id())
            track_total_score = track.add_score(1)
            logging.info("DromedarisRace: Track ID:%s Sensor:%s TotalScore:%s" %(track.get_track_id(), sensor_event.get_sensor_id(), track_total_score))
            return track

        return None

    def __run(self):
        sensor_poller = self.sensor_container.get_sensor_poller()
        sensor_poller.start()

        track = self.__process_sensor_events()
        if (track != None):
            self.track_container.print_score_overview() # Score has changed, so print score overview.
            if (track.reached_max_score() == True):
                logging.info("DromedarisRace: Winner is Track ID:{:02} Total Score:{:02}".format(track.get_track_id(), track.get_score()))
                self.__pause()

    def __pause(self):
        sensor_poller = self.sensor_container.get_sensor_poller()
        sensor_poller.stop()

        self.track_container.pause_motors()

    def __reset(self):
        self.__pause()

        while not self.sensor_event_queue.empty():
            self.sensor_event_queue.get()

        self.track_container.reset_scores()


    def main(self) -> None:
        logging.debug("DromedarisRace: Running main")

        while (True):
            self.__run()


# Run Main
if (__name__ == "__main__"):
    try:
        DromedarisRace().main()

    except KeyboardInterrupt:
        logging.info("Ctrl + C: Exiting program")
        GPIO.cleanup()
