import logging, sys
import threading, queue
import time
import smbus

from ThrowingTrack import ThrowingTrack
from Sensor import MicroSwitch, SensorContainer, SensorEvent, EdgeEventEnum
from IOExtender import MCP23017

# Setup Logging Parameters
logging.basicConfig(stream=sys.stderr, level=logging.INFO)


# Setup Main Class
class KamelenRace:
    def __init__(self) -> None:
        logging.debug("KamelenRace: Initializing")

        self.I2CBus = smbus.SMBus(1)
        self.EXTENDER_MAPPING = ( MCP23017(self.I2CBus, 0x20, 0xFF, 0xFF), )#MCP23017(self.I2CBus, 0x21, 0xFF, 0xFF) )
        self.SENSOR_MAPPING   = ( MicroSwitch(0x01, 0x01, 0x20, 0x00), MicroSwitch(0x01, 0x02, 0x20, 0x01), MicroSwitch(0x01, 0x03, 0x20, 0x02) )
        self.NUMBER_OF_TRACKS = 2
        self.START_SCORE = 0
        self.MAX_SCORE = 25

        self.sensor_event_queue = queue.Queue()
        self.sensor_container = SensorContainer(self.EXTENDER_MAPPING, self.SENSOR_MAPPING, self.sensor_event_queue)
        self.track_container = list()
        for i in range(0, self.NUMBER_OF_TRACKS):
            self.track_container.append(ThrowingTrack(i, self.START_SCORE, self.MAX_SCORE))

        time.sleep(2) # TODO: debug time out

    def __sensor_events_process(self) -> None:
        while (True):
            sensor_event = self.sensor_event_queue.get()

            if (EdgeEventEnum.EDGE_DETECT_RISING == sensor_event.get_edge_event()):
                track = self.track_container[sensor_event.get_track_id()]
                track_total_score = track.add_score(1)
                logging.info("Rising Edge: TRACK ID:%s TotalScore:%s" %(track.get_track_id(), track_total_score))
                
                if (track_total_score >= self.MAX_SCORE):
                    logging.info("KamelenRace: WINNER IS TRACK ID:%s" %(track.get_track_id()))

                    for track in self.track_container:
                        pass # print all scores

                    break


    def main(self) -> None:
        logging.debug("KamelenRace: Running main")

        sensor_poller = self.sensor_container.get_sensor_poller()
        sensor_poller.start()
        time.sleep(2)
        #sensor_poller.stop()

        self.__sensor_events_process()



# Run Main 
if (__name__ == "__main__"):
    game = KamelenRace()
    game.main()
