import threading, queue

import logging, sys
import time 
from enum import Enum

from IOExtender import ExtenderContainer

class EdgeEventEnum(Enum):
    EDGE_DETECT_NONE = 0
    EDGE_DETECT_RISING = 1
    EDGE_DETECT_FALLING = 2

class SensorEvent:
    def __init__(self, track_id, sensor_id, edge_event) -> None:
        self.track_id = track_id
        self.sensor_id = sensor_id
        self.edge_event = edge_event

    def get_track_id(self) -> int:
        return self.track_id

    def get_sensor_id(self) -> int:
        return self.sensor_id

    def get_edge_event(self) -> int:
        return self.edge_event


class MicroSwitch:
    def __init__(self, track_id, sensor_id, device_addr, pin_number, debounce_time_ms) -> None:
        logging.debug("MicroSwitch: Initializing Track:{:02} Sensor:{:02} (DEV:0x{:02X} PIN:{:02})".format(track_id, sensor_id, device_addr, pin_number))
        self.track_id = track_id
        self.sensor_id = sensor_id
        self.device_addr = device_addr
        self.pin_number = pin_number
        self.previous_value = True
        self.previous_update_time_ms = 0
        self.debounce_time_out_ms = debounce_time_ms

    def update(self, updated_value) -> SensorEvent:
        pin_num = self.get_pin_number() % 8
        updated_bool = bool(updated_value & (1 << pin_num))

        current_time_ms = time.time() * 1000
        delta_time_ms = current_time_ms - self.previous_update_time_ms 

        event = EdgeEventEnum.EDGE_DETECT_NONE
        if ((updated_bool == True and self.previous_value == False) and delta_time_ms > self.debounce_time_out_ms):
            event = EdgeEventEnum.EDGE_DETECT_RISING
            self.previous_update_time_ms = current_time_ms
            self.previous_value = updated_bool
        elif ((updated_bool == False and self.previous_value == True) and delta_time_ms > self.debounce_time_out_ms):
            event = EdgeEventEnum.EDGE_DETECT_FALLING
            self.previous_update_time_ms = current_time_ms
            self.previous_value = updated_bool

        #logging.debug("Polling MicroSwitch ID:%s (%s)" %(self.sensor_id, event.name)) # DEBUG: ENABLE IF NEEDED
        return SensorEvent(self.track_id, self.sensor_id, event)

    def get_track_id(self) -> int:
        return self.track_id

    def get_sensor_id(self) -> int:
        return self.sensor_id

    def get_device_addr(self) -> int:
        return self.device_addr

    def get_pin_number(self) -> int:
        return self.pin_number



class SensorContainer:
    def __init__(self, extender_mapping, sensor_mapping, sensor_event_queue) -> None:
        logging.debug("SensorContainer: Initializing")

        self.extender_container = ExtenderContainer(extender_mapping)
        self.sensor_container = sensor_mapping
        self.sensor_poller = SensorPoller(self.__on_poll_callback)
        self.sensor_event_queue = sensor_event_queue

    def __on_poll_callback(self):
        extender_poll_result = self.extender_container.poll()
        for result in extender_poll_result:
            self.__update_sensor(result[0], result[1], result[2])

    def __update_sensor(self, device_addr, reg_a, reg_b):
        for sensor in self.sensor_container:
            if (sensor.get_device_addr() == device_addr):
                if (sensor.get_pin_number() <= 8):
                    self.__update_event_queue(sensor.update(reg_a))
                else:
                    self.__update_event_queue(sensor.update(reg_b))

    def __update_event_queue(self, sensor_event):
        if (sensor_event.get_edge_event() == EdgeEventEnum.EDGE_DETECT_FALLING):
            self.sensor_event_queue.put(sensor_event)
        #elif (sensor_event.get_edge_event() == EdgeEventEnum.EDGE_DETECT_RISING):
        #    self.sensor_event_queue.put(sensor_event)
        # elif (sensor_event.get_edge_event() == EdgeEventEnum.EDGE_DETECT_NONE):
        #     self.sensor_event_queue.put(sensor_event)

    def get_sensor_poller(self):
        return self.sensor_poller


class SensorPoller:
    def __init__(self, callback) -> None:
        logging.debug("SensorPoller: Initializing")
        self.polling_thread_running = threading.Event()
        self.polling_thread = threading.Thread(target=self.__polling_thread, args=(self.polling_thread_running,))
        self.callback = callback

    def __polling_thread(self, thread_running) -> None:
        while (self.polling_thread_running.is_set()):
            logging.debug("SensorPoller: Polling callback")
            self.callback()

    def start(self) -> None:
        logging.debug("SensorPoller: Starting polling thread")
        self.polling_thread_running.set()
        self.polling_thread = threading.Thread(target=self.__polling_thread, args=(self.polling_thread_running,))
        self.polling_thread.start()

    def stop(self) -> None:
        logging.info("SensorPoller: Stopping polling thread")
        self.polling_thread_running.clear()
        self.polling_thread.join()
