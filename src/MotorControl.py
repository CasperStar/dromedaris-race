import logging, threading, queue
from enum import Enum
from collections import namedtuple
from time import sleep

from IOControl import GLOBAL_I2C_BUS

class MotorActionEnum(Enum):
    STOP_PASSIVE = 0
    TURN_CLOCKWISE = 1
    TURN_ANTI_CLOCKWISE = 2
    STOP_ACTIVE = 3

class MotorController():
    def __init__(self, address: int):
        logging.debug(f"{type(self).__name__}: Initializing")
        self.bus = GLOBAL_I2C_BUS
        self.controller_address = address

    def set_motor_speed(self, motor_id: int, speed: int):
        logging.debug(f"{type(self).__name__}: Setting Motor {motor_id} Speed {speed}")
        self.bus.write_block_data(self.controller_address, motor_id, [0x010, speed])

    def set_motor_action(self, motor_id: int, action: MotorActionEnum):
        logging.debug(f"{type(self).__name__}: Setting Motor {motor_id} Action {action}")
        self.bus.write_block_data(self.controller_address, motor_id, [0x020, action.value])


MotorQueueInfo = namedtuple('MotorQueueInfo', ['action', 'speed', 'ms'])

class Motor():
    def __init__(self, controller: MotorController, motor_id: int):
        logging.debug(f"{type(self).__name__}: Initializing")
        self.controller = controller
        self.motor_id = motor_id

        self.thread_queue = queue.Queue()
        self.thread_running = threading.Event()
        self.thread_pausing = threading.Event()
        self.thread = threading.Thread(target = self.thread_worker, args = ())
        self.start_thread()

    def thread_worker(self):
        logging.debug(f"{type(self).__name__}: Thread Worker Starting {self.motor_id}")

        is_motor_stopped = False
        while (self.thread_running.is_set()):

            # Running Logic
            if not self.thread_queue.empty():
                is_motor_stopped = False

                run_info = self.thread_queue.get()
                self.controller.set_motor_speed(self.motor_id, run_info.speed)
                self.controller.set_motor_action(self.motor_id, run_info.action)
                sleep(run_info.ms / 1000)
            elif (not is_motor_stopped):
                self.controller.set_motor_action(self.motor_id, MotorActionEnum.STOP_PASSIVE)
                is_motor_stopped = True

            # Pausing Logic
            if (not is_motor_stopped and self.thread_pausing.is_set()):
                self.controller.set_motor_action(self.motor_id, MotorActionEnum.STOP_PASSIVE)
                is_motor_stopped = True

            while (self.thread_pausing.is_set()):
                pass

        logging.debug(f"{type(self).__name__}: Thread Worker Stopping {self.motor_id}")

    def run_for(self, action: MotorActionEnum, speed: int, ms: int):
        info = MotorQueueInfo(action, speed, ms)
        logging.debug(f"{type(self).__name__}: Adding Motor {self.motor_id} Event to Queue. Action:{action} Speed:{speed} Duration:{ms}")
        self.thread_queue.put(info)

    def stop_thread(self):
        logging.debug(f"{type(self).__name__}: Stop Thread {self.motor_id}")
        self.thread_running.clear()
        self.thread.join()

    def start_thread(self):
        logging.debug(f"{type(self).__name__}: Start Thread {self.motor_id}")
        self.thread_running.set()
        self.thread_pausing.clear()
        if (not self.thread.is_alive()):
            self.thread.start()

    def pause_thread(self):
        logging.debug(f"{type(self).__name__}: Pausing Thread {self.motor_id}")
        self.thread_pausing.set()

    def all_events_processed(self) -> bool:
        return self.thread_queue.empty()
