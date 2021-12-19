import yaml
import logging
from collections import namedtuple


from IOExtender import MCP23017
from Sensor import MicroSwitch
from Lane import Lane
from MotorControl import MotorController, Motor
from Button import Button
from Led import Led


Config = namedtuple("Config", ["LaneMapping", "ExtenderMapping", "SensorMapping", "ButtonMapping", "LedMapping"])

class ConfigLoader:

    def __init__(self):
        logging.debug(f"{type(self).__name__}: Initializing")
        self._lane_mapping = list()
        self._extender_mapping = list()
        self._sensor_mapping = list()
        self._button_mapping  = list()
        self._led_mapping  = list()

    def load_config(self, config_path):
        try:
            with open(config_path) as stream:
                data_map = yaml.safe_load(stream)

            motor_controller_address = data_map.get("MotorController").get('Address')
            motor_controller = MotorController(motor_controller_address)

            lane_mapping = data_map.get("LaneMapping")
            self.process_lane_mapping(lane_mapping, motor_controller)

            extender_mapping = data_map.get("ExtenderMapping")
            self.process_extender_mapping(extender_mapping)

            sensor_mapping = data_map.get("SensorMapping")
            (self.process_sensor_mapping(sensor_mapping))

            button_mapping = data_map.get("ButtonMapping")
            self.process_button_mapping(button_mapping)

            led_mapping = data_map.get("LedMapping")
            self.process_led_mapping(led_mapping)

        except yaml.YAMLError as exception:
            print(exception)
            exit(-1)

    def get_loaded_config(self) -> Config:
        config = Config(self._lane_mapping, self._extender_mapping, self._sensor_mapping, self._button_mapping, self._led_mapping)
        logging.debug(f"{type(self).__name__}: Returned Config: {config}")
        return config


    def process_lane_mapping(self, mapping, motor_controller):
        for lane in mapping:
            lane_data = lane.get('Lane')
            if (lane_data != None):
                self._lane_mapping.append(self.construct_lane(lane_data, motor_controller))

    def process_extender_mapping(self, mapping):
        for extender in mapping:
            extender_data = extender.get('MCP23017')
            if (extender_data != None):
                self._extender_mapping.append(self.construct_mcp23017(extender_data))

    def process_sensor_mapping(self, mapping):
        for sensor in mapping:
            sensor_data = sensor.get('MicroSwitch')
            if (sensor_data != None):
                self._sensor_mapping.append(self.construct_microswitch(sensor_data))

    def process_button_mapping(self, mapping):
        for button in mapping:
            button_data = button.get('Button')
            if (button_data != None):
                self._button_mapping.append(self.construct_button(button_data))

    def process_led_mapping(self, mapping):
        for led in mapping:
            led_data = led.get('Led')
            if (led_data != None):
                self._led_mapping.append(self.construct_led(led_data))
                continue


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    def construct_lane(self, data, motor_controller) -> Lane:
        lane_id     = data.get("LaneId")
        score_start = data.get("ScoreStart")
        score_end   = data.get("ScoreEnd")
        motor_speed = data.get("MotorSpeedPct")
        motor_run_duration = data.get("MotorRunDurationMs")

        motor = Motor(motor_controller, lane_id) # Lane id is same as motor id

        logging.debug(f"{type(self).__name__}: Constructing Lane {lane_id}, {score_start}, {score_end}, {motor}")
        return Lane(lane_id, score_start, score_end, motor, motor_speed, motor_run_duration)

    def construct_mcp23017(self, data) -> MCP23017:
        device_address  = data.get("DeviceAddress")
        reg_a_direction = data.get("RegisterA").get("Direction")
        reg_a_pullup    = data.get("RegisterA").get("Pullup")
        reg_b_direction = data.get("RegisterB").get("Direction")
        reg_b_pullup    = data.get("RegisterB").get("Pullup")

        logging.debug(f"{type(self).__name__}: Constructing MCP23017 {device_address}, {reg_a_direction}, {reg_a_pullup}, {reg_b_direction}, {reg_b_pullup}")
        return MCP23017(device_address, reg_a_direction, reg_a_pullup, reg_b_direction, reg_b_pullup)

    def construct_microswitch(self, data) -> MicroSwitch:
        track_id    = data.get("TrackId")
        sensor_id   = data.get("SensorId")
        device_addr = data.get("DeviceAddress")
        pin_number  = data.get("PinNumber")
        debounce_time_ms = data.get("DebounceDelay")
 
        logging.debug(f"{type(self).__name__}: Constructing MicroSwitch {track_id}, {sensor_id}, {device_addr}, {pin_number}, {debounce_time_ms}") 
        return MicroSwitch(track_id, sensor_id, device_addr, pin_number, debounce_time_ms)

    def construct_button(self, data) -> Button:
        button_id   = data.get("ButtonId")
        device_addr = data.get("DeviceAddress")
        pin_number  = data.get("PinNumber")

        logging.debug(f"{type(self).__name__}: Constructing Button {button_id}, {device_addr}, {pin_number}")
        return Button(button_id, device_addr, pin_number)

    def construct_led(self, data) -> Led:
        led_id   = data.get("LedId")
        device_addr = data.get("DeviceAddress")
        pin_number  = data.get("PinNumber")

        logging.debug(f"{type(self).__name__}: Constructing LED {led_id}, {device_addr}, {pin_number}")
        return Led(led_id, device_addr, pin_number)

