import logging, sys
import threading, queue
import time
import smbus

from ThrowingTrack import ThrowingTrack, TrackContainer
from Sensor import MicroSwitch, SensorContainer, SensorEvent, EdgeEventEnum
from IOExtender import MCP23017, ExtenderPin
from MotorController import MotorController

# Setup Logging Parameters
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

GLOBAL_I2C_BUS = smbus.SMBus(1)
GLOBAL_EXTENDER_MAPPING = ( MCP23017(GLOBAL_I2C_BUS, 0x20, 0b00111111, 0b00111111), # Track 1 - Track 4 
                            MCP23017(GLOBAL_I2C_BUS, 0x21, 0b00111111, 0b00000111), # Track 5 - Track 6
                            MCP23017(GLOBAL_I2C_BUS, 0x22, 0b00000000, 0b00000000)) # Motor 1 - Motor 6

GLOBAL_SENSOR_MAPPING = ( MicroSwitch(1, 1, 0x20,  0), MicroSwitch(1, 2, 0x20,  1), MicroSwitch(1, 3, 0x20,  2), # Track 1 
                          MicroSwitch(2, 1, 0x20,  3), MicroSwitch(2, 2, 0x20,  4), MicroSwitch(2, 3, 0x20,  5)) # Track 2
                         #MicroSwitch(3, 1, 0x20,  8), MicroSwitch(3, 2, 0x20,  9), MicroSwitch(3, 3, 0x20, 10), # Track 3
                         #MicroSwitch(4, 1, 0x20, 11), MicroSwitch(4, 2, 0x20, 12), MicroSwitch(4, 3, 0x20, 13), # Track 4
                         #MicroSwitch(5, 1, 0x21,  0), MicroSwitch(5, 2, 0x21, 01), MicroSwitch(5, 3, 0x21,  2), # Track 5
                         #MicroSwitch(6, 1, 0x21,  3), MicroSwitch(6, 2, 0x21, 04), MicroSwitch(6, 3, 0x21,  5), # Track 6

GLOBAL_MOTOR_MAPPING = ( MotorController(1, 18, 100, ExtenderPin(0x22,  0), ExtenderPin(0x22,  1)), # Track 1 
                         MotorController(2, 18, 100, ExtenderPin(0x22,  2), ExtenderPin(0x22,  3)), # Track 2
                         MotorController(3, 18, 100, ExtenderPin(0x22,  4), ExtenderPin(0x22,  5)), # Track 3
                         MotorController(4, 18, 100, ExtenderPin(0x22,  6), ExtenderPin(0x22,  7)), # Track 4
                         MotorController(5, 18, 100, ExtenderPin(0x22,  8), ExtenderPin(0x22,  9)), # Track 5
                         MotorController(6, 18, 100, ExtenderPin(0x22, 10), ExtenderPin(0x22, 11))) # Track 6

# Setup Main Class
class DromedarisRace:
    def __init__(self) -> None:
        logging.debug("DromedarisRace: Initializing")

        self.NUMBER_OF_TRACKS = 6
        self.START_SCORE      = 0
        self.MAX_SCORE        = 25

        self.sensor_event_queue = queue.Queue()
        self.sensor_container = SensorContainer(GLOBAL_EXTENDER_MAPPING, GLOBAL_SENSOR_MAPPING, self.sensor_event_queue)
        self.track_container = TrackContainer(self.NUMBER_OF_TRACKS, self.START_SCORE, self.MAX_SCORE)

    def __process_sensor_events(self):
        sensor_event = self.sensor_event_queue.get()

        if (EdgeEventEnum.EDGE_DETECT_RISING == sensor_event.get_edge_event()):
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
            self.print_score_overview() # Score has changed, so print score overview.
            if (track.reached_max_score()):
                logging.info("DromedarisRace: Winner is Track ID:{:02s} Total Score:{:02s}".format(track.get_track_id(), track.get_score()))
                self.__pause()

    def __pause(self):
        sensor_poller = self.sensor_container.get_sensor_poller()
        sensor_poller.stop()

    def __reset(self):
        self.__pause()

        while not self.sensor_event_queue.empty():
            self.sensor_event_queue.get()

        self.track_container.reset_scores()


    def main(self) -> None:
        logging.debug("DromedarisRace: Running main")

        while (True):
            self.run()



# Run Main
if (__name__ == "__main__"):
    game = DromedarisRace()
    game.main()
