import logging, sys
import threading, queue, time

from IORaspberry import RaspberryPin, RaspberryPinPWM, IODirection
from enum import Enum

class TurnDirection(Enum):
    CLOCKWISE = 1
    ANTI_CLOCKWISE = 2

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Direct Current Motor Code (using L298Ns a Controller)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class DCMotor():
    def __init__(self, motor_id, pwm_pin, dir_pin_1, dir_pin_2) -> None:
        logging.debug("DCMotor: Initializing {:02}".format(motor_id))
        self.motor_id = motor_id
        self.pwm_pin  = pwm_pin
        self.direction_pin_1 = dir_pin_1
        self.direction_pin_2 = dir_pin_2
        self.stop()

        self.run_async_queue = queue.Queue()
        self.async_running_thread_running = threading.Event()
        self.async_running_thread_pausing = threading.Event()

        self.start_async_thread()
        self.async_running_thread = threading.Thread(target = self.__process_async_running_thread, args = ())
        self.async_running_thread.start()

    def start(self, turn_direction, speed):
        logging.debug("DCMotor: Motor {:02} running {} at {:02}%".format(self.motor_id, turn_direction.name, speed))
        self.set_direction(turn_direction)
        self.pwm_pin.start(speed)

    def stop(self):
        logging.debug("DCMotor: Motor {:02} stopping".format(self.motor_id))
        self.direction_pin_1.set(False)
        self.direction_pin_2.set(False)
        self.pwm_pin.stop()

    def set_speed(self, speed):
        logging.debug("DCMotor: Motor {:02} set speed {:02}%".format(self.motor_id, speed))
        self.pwm_pin.set_duty_cycle(speed)

    def set_direction(self, turn_direction):
        logging.debug("DCMotor: Motor {:02} set direction {}".format(self.motor_id, turn_direction.name))
        if (TurnDirection.CLOCKWISE == turn_direction):
            self.direction_pin_1.set(True)
            self.direction_pin_2.set(False)
        elif (TurnDirection.ANTI_CLOCKWISE == turn_direction):
            self.direction_pin_1.set(False)
            self.direction_pin_2.set(True)

    def run_async(self, turn_direction, speed, time_in_ms):
        logging.debug("DCMotor: Motor {:02} Posting to async queue ({} {}% {}ms)".format(self.motor_id, turn_direction.name, speed, time_in_ms))
        self.run_async_queue.put((turn_direction, speed, time_in_ms))

    def __process_async_running_thread(self):
        while (self.async_running_thread_running.is_set()):
            if not self.run_async_queue.empty():
                run_info = self.run_async_queue.get()
                
                self.start(run_info[0], run_info[1])
                time.sleep(run_info[2] / 1000)

                if self.run_async_queue.empty():
                    self.stop()
            else:
                while (self.async_running_thread_pausing.is_set()):
                    pass

    def start_async_thread(self):
        logging.debug("DCMotor: Motor {:02} Starting thread".format(self.motor_id))
        self.async_running_thread_running.set()

    def stop_async_thread(self):
        logging.debug("DCMotor: Motor {:02} Stopping thread".format(self.motor_id))
        self.async_running_thread_running.clear()
        self.async_running_thread.join()

    def pause_async_thread(self):
        logging.debug("DCMotor: Motor {:02} Pausing thread".format(self.motor_id))
        self.async_running_thread_pausing.set()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Stepper Motor Code
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

REVOLUTION_IN_DEGREES = 360
NUMBER_OF_HALF_STEPS_PER_REV = 4096
HALF_STEP_SEQUENCE = ((1,0,0,0),
                      (1,1,0,0),
                      (0,1,0,0),
                      (0,1,1,0),
                      (0,0,1,0),
                      (0,0,1,1),
                      (0,0,0,1),
                      (1,0,0,1))

NUMBER_OF_FULL_STEPS_PER_REV = 2048
FULL_STEP_SEQUENCE = ((1,0,0,0),
                      (0,1,0,0),
                      (0,0,1,0),
                      (0,0,0,1))

class StepperMotor:
    def __init__(self, delay, pin1, pin2, pin3, pin4) -> None:
        logging.debug("StepperMotor: Initializing")
        self.step_delay = delay
        self.current_step = 0
        self.step_sequence = FULL_STEP_SEQUENCE
        self.NUMBER_OF_STEPS_PER_REV = NUMBER_OF_FULL_STEPS_PER_REV
        self.total_steps = 0
        self.pins = [pin1, pin2, pin3, pin4]

        #self.I2CBus = smbus.SMBus(1)
        #self.mcp = MCP23017(self.I2CBus, 0x20, 0x00, 0x00)

    def set_step_delay(self, delay) -> None:
        self.step_delay = delay

    def __turn_step(self, direction):
        # Setting ULN2003 pin to next sequence step
        logging.debug("StepperMotor: Set sequence: {} {} ({})".format(self.current_step, self.step_sequence[self.current_step], self.total_steps))

        register_byte = 0
        for index, seq_value in enumerate(self.step_sequence[self.current_step]):
            if seq_value == 1:
                register_byte |=  (1 << self.pins[index]) # Set bit
            elif seq_value == 0:
                register_byte &= ~(1 << self.pins[index]) # Clear bit

        # Write sequence to IO
        logging.debug("Written Byte: {0:08b}".format(register_byte))
        #self.mcp.write_register_a(register_byte)


        if (TurnDirection.CLOCKWISE == direction):
            self.current_step += 1
            self.total_steps += 1
        elif (TurnDirection.ANTI_CLOCKWISE == direction):
            self.current_step -= 1
            self.total_steps -= 1

        if (self.current_step >= len(self.step_sequence)):
            self.current_step = 0
        elif (self.current_step < 0):
            self.current_step = len(self.step_sequence) - 1

        time.sleep(self.step_delay)


    def turn_steps(self, direction, steps) -> None:
        logging.debug("StepperMotor: Turn steps: {} {}".format(steps, direction.name))
        for i in range(self.current_step, self.current_step + steps):
            self.__turn_step(direction)

    def turn_degrees(self, direction, degrees) -> None:
        needed_steps = degrees * (self.NUMBER_OF_STEPS_PER_REV / REVOLUTION_IN_DEGREES)
        logging.debug("StepperMotor: Turn degrees: {} {} (Steps: {:4.2f})".format(degrees, direction.name, needed_steps))
        self.turn_steps(direction, int(needed_steps))
