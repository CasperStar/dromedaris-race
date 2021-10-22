import yaml
import logging

from collections import namedtuple

Config = namedtuple("Config", ["LaneMapping", "ExtenderMapping", "SensorMapping", "MotorMapping"])

class ConfigLoader:

    def __init__(self):
        self._extender_mapping = list()
        self._sensor_mapping = list()

    def LoadConfig(self, config_path):
        try:
            with open(config_path) as stream:
                dataMap = yaml.safe_load(stream)

            extender_mapping = dataMap.get("ExtenderMapping")
            self.ProcessExtenderMapping(extender_mapping)

            sensor_mapping = dataMap.get("SensorMapping")
            (self.ProcessSensorMapping(sensor_mapping))


        except yaml.YAMLError as exception:
            print(exception)
            exit(-1)

    def GetLoadedConfig(self) -> Config:

        return Config(1, self._extender_mapping, self._sensor_mapping, 2)

    def ProcessExtenderMapping(self, mapping):
        for extender in mapping:
            extender_data = extender.get('MCP23017')
            if (extender_data != None):
                self._extender_mapping.append(self.ConstructMCP23017(extender_data))
                continue

    def ProcessSensorMapping(self, mapping):
        for sensor in mapping:
            sensor_data = sensor.get('MicroSwitch')
            if (sensor_data != None):
                self._sensor_mapping.append(self.ConstructMicroSwitch(sensor_data))
                continue


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    def ConstructMCP23017(self, data) -> int:
        device_address  = data.get("DeviceAddress")
        reg_a_direction = data.get("RegisterA").get("Direction")
        reg_a_pullup    = data.get("RegisterA").get("Pullup")
        reg_b_direction = data.get("RegisterB").get("Direction")
        reg_b_pullup    = data.get("RegisterB").get("Pullup")

        logging.debug(f"{type(self).__name__}: Constructing MCP23017 {device_address}, {reg_a_direction}, {reg_a_pullup}, {reg_b_direction}, {reg_b_pullup}")
        #return MCP23017(device_address, reg_a_direction, reg_a_pullup, reg_a_pullup, reg_b_direction, reg_b_pullup)
        return 111

    def ConstructMicroSwitch(self, data):
        track_id    = data.get("TrackId")
        sensor_id   = data.get("SensorId")
        device_addr = data.get("DeviceAddress")
        pin_number  = data.get("PinNumber")
        debounce_time_ms = data.get("DebounceDelay")
 
        logging.debug(f"{type(self).__name__}: Constructing MicroSwitch {track_id}, {sensor_id}, {device_addr}, {pin_number}, {debounce_time_ms}") 
        #return MicroSwitch(track_id, sensor_id, device_addr, pin_number, debounce_time_ms)
        return 222

