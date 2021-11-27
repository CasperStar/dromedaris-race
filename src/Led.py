import logging, sys

from IOExtender import ExtenderPin, IODirection

class Led():
    def __init__(self, led_id, device_addr, pin_number):
        logging.debug(f"{type(self).__name__}: Initializing")
        self.extender_pin = ExtenderPin(device_addr, pin_number, IODirection.OUTPUT)
        self.TurnOff()

    def TurnOn(self):
        self.extender_pin.set(True)

    def TurnOff(self):
        self.extender_pin.set(False)
