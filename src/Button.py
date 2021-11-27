import threading, queue

import logging, sys
import time

from IOExtender import ExtenderPin, IODirection

class Button():
    def __init__(self, button_id, device_addr, pin_number):
        logging.debug(f"{type(self).__name__}: Initializing")
        self.extender_pin = ExtenderPin(device_addr, pin_number, IODirection.INPUT)
        pass

    def IsActive(self) -> bool:
        value = self.extender_pin.get()
        return not(value)