import logging
from IOControl import IODirection, DigitalPin

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)

class RaspberryPin(DigitalPin):
    def __init__(self, pin, direction) -> None:
        logging.debug("RaspberryPin: Initializing PIN:{:02} DIR:{}".format(pin, direction.name))
        self.pin = pin
        self.direction = direction
        if (self.direction == IODirection.INPUT):
            GPIO.setup(self.pin, GPIO.IN)
        elif (self.direction == IODirection.OUTPUT):
            GPIO.setup(self.pin, GPIO.OUT)

    def set(self, value):
        if (self.direction == IODirection.OUTPUT):
            GPIO.output(self.pin, value)
        else:
            raise Exception("RaspberryPin: Writing PIN:{:02} while it is an input!".format(self.pin))

    def get(self):
        return GPIO.input(self.pin)

class RaspberryPinPWM():
    def __init__(self, pin, frequency_hz) -> None:
        logging.debug("RaspberryPinPWM: Initializing PIN:{:02} on {:03}Hz".format(pin, frequency_hz))
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm_pin = GPIO.PWM(self.pin, frequency_hz)

    def start(self, duty_cycle):
        self.pwm_pin.start(duty_cycle)

    def stop(self):
        self.pwm_pin.stop()

    def set_frequency(self, frequency_hz):
        self.pwm_pin.ChangeFrequency(frequency_hz)

    def set_duty_cycle(self, duty_cycle):
        self.pwm_pin.ChangeDutyCycle(duty_cycle)