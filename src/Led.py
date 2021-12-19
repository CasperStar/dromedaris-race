import logging, sys
import time
from IOExtender import ExtenderPin, IODirection

class Led():
    def __init__(self, led_id, device_addr, pin_number):
        logging.debug(f"{type(self).__name__}: Initializing")
        self.extender_pin = ExtenderPin(device_addr, pin_number, IODirection.OUTPUT)
        self.turn_off()

    def turn_on(self):
        self.extender_pin.set(True)

    def turn_off(self):
        self.extender_pin.set(False)

    def turn_on_for(self, ms:int):
        self.turn_on()
        time.sleep(ms/1000)
        self.turn_off()