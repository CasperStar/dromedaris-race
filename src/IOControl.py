
import logging, random, sys
import abc
from enum import Enum

class IODirection(Enum):
    OUTPUT = 0
    INPUT  = 1

class DigitalPin(abc.ABC):
    @abc.abstractmethod
    def set(self, value):
        pass

    @abc.abstractmethod
    def get(self):
        pass



