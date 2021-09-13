
import logging, random
import smbus

class ExtenderContainer:
    def __init__(self, extender_mapping) -> None:
        logging.debug("ExtenderContainer: Initializing")

        self.io_extenders = extender_mapping

    def poll(self):
        result = list()
        for extender in self.io_extenders:
            polling_result = (extender.get_device_addr(), extender.poll_register_a(), extender.poll_register_b())
            result.append(polling_result)

        return result

class MCP23017:
    IODIRA = 0x00 # Pin direction register A
    IODIRB = 0x01 # Pin direction register B
    GPPUA  = 0x0C # Pull-up Resistor Register A
    GPPUB  = 0x0D # Pull-up Resistor Register B
    GPIOA  = 0x12 # Pin I/O Register A
    GPIOB  = 0x13 # Pin I/O Register B
    OLATA  = 0x14 # OUTPUT LATCH REGISTER A
    OLATB  = 0x15 # OUTPUT LATCH REGISTER A

    def __init__(self, bus, device_addr, io_direction_a, io_direction_b) -> None:
        logging.debug("MCP23017: ID:%s Initializing" %(device_addr))
        self.device_addr = device_addr
        self.bus = bus
        self.io_direction_a = io_direction_a
        self.io_direction_b = io_direction_b

        self.bus.write_byte_data(device_addr, self.IODIRA, io_direction_a)
        self.bus.write_byte_data(device_addr, self.GPPUA, io_direction_a)
        self.bus.write_byte_data(device_addr, self.IODIRB, io_direction_b)
        self.bus.write_byte_data(device_addr, self.GPPUB, io_direction_b)

    def get_device_addr(self):
        return self.device_addr

    def poll_register_a(self):
        register_a = self.bus.read_byte_data(self.device_addr, self.GPIOA)
        logging.debug("MCP23017: ID:%s Polling register A (%s)" %(self.device_addr, format(register_a, '#010b')))
        return register_a

    def poll_register_b(self):
        register_b = self.bus.read_byte_data(self.device_addr, self.GPIOB)
        logging.debug("MCP23017: ID:%s Polling register B (%s)" %(self.device_addr, format(register_b, '#010b')))
        return register_b

    def write_register_a(self, byte):
        byte_to_write = byte & ~(self.io_direction_a) # Ensure only outputs will be written
        logging.debug("MCP23017: ID:{} Writing register A ({:08b})".format(self.device_addr, byte_to_write))
        self.bus.write_byte_data(self.device_addr, self.OLATA, byte_to_write)
    
    def write_register_b(self, byte):
        byte_to_write = byte & ~(self.io_direction_b) # Ensure only outputs will be written
        logging.debug("MCP23017: ID:{} Writing register B ({:08b})".format(self.device_addr, byte_to_write))
        self.bus.write_byte_data(self.device_addr, self.OLATB, byte_to_write)

    