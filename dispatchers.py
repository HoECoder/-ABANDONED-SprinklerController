import logging

HAS_GPIO = True

try:
    import pigpio
except ImportError:
    HAS_GPIO = False

# I'm assuming a RPi A+/B+ or RPi 2
# Swiped the definition from OpenSprinkler Unified Firmware
# OpenSprinkler-Firmware/defines.h
# https://github.com/OpenSprinkler/OpenSprinkler-Firmware/blob/a62856969722f8185b1168737b67d8497ffb95b2/defines.h#L307
pin_sr_dat = 27 # Shift Register Data Pin
pin_sr_clk = 4  # Shift Register Clock Pin
pin_sr_oe = 17  # Shift Register Output Enable Pin
pin_sr_lat = 22 # Shift Register Latch Pin
gpio_pins = [pin_sr_dat,
             pin_sr_clk,
             pin_sr_oe,
             pin_sr_lat]
gpio_pin_names = {pin_sr_dat : "pin_sr_dat",
                  pin_sr_clk : "pin_sr_clk",
                  pin_sr_oe : "pin_sr_oe",
                  pin_sr_lat : "pin_sr_lat"}
gpio_pin_help = {pin_sr_dat : "SR Data",
                 pin_sr_clk : "SR Clock",
                 pin_sr_oe : "SR Output Enable",
                 pin_sr_lat : "SR Latch"}

class GenericDispatcher(object):
    def enable_shift_register(self):
        pass
    def disable_shift_register(self):
        pass
    def write_register(self,bit_pattern):
        pass
    def write_pattern_to_register(self,bit_pattern):
        self.disable_shift_register()
        self.write_register(bit_pattern)
        self.enable_shift_register()

class GPIODispatcher(GenericDispatcher):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.gpio = pigpio.pi()
        if not self.gpio is None:
            self.__setup_pins()
        else:
            self.logger.critical("Failed to get GPIO!")
    def __setup_pins(self):
        self.logger.debug("Setting pin mode to pigpio.OUTPUT")
        self.gpio.set_mode(pin_sr_oe,pigpio.OUTPUT)
	self.gpio.set_mode(pin_sr_clk, pigpio.OUTPUT)
	self.gpio.set_mode(pin_sr_dat, pigpio.OUTPUT)
	self.gpio.set_mode(pin_sr_lat, pigpio.OUTPUT)
	self.logger.debug("Writing the proper pin levels")
	self.gpio.write(pin_sr_oe, 1)
	self.gpio.write(pin_sr_clk, 0)
	self.gpio.write(pin_sr_dat, 0)
	self.gpio.write(pin_sr_lat, 0)
	self.logger.info("Pins %s setup.", str(gpio_pins))
	
    def __enable_disable_sr(self, bit):
        self.gpio.write(pin_sr_oe,bit)
    def enable_shift_register(self):
        self.__enable_disable_sr(0)
        self.logger.info("Enabled Shift Register")
    def disable_shift_register(self):
        self.__enable_disable_sr(1)
        self.logger.info("Disabled Shift Register")
    def write_register(self,bit_pattern):
        self.logger.debug("Writing Bit Pattern %s", str(bit_pattern))
        self.gpio.write(pin_sr_clk,0)
	self.gpio.write(pin_sr_lat,0)
	# Bit bang the pattern in, top bit first
	bits = list(bit_pattern)
	bits.reverse()
	self.logger.debug("Bit Order %s",str(bits))
	for bit in bits:
		self.gpio.write(pin_sr_clk,0)
		self.gpio.write(pin_sr_dat,bit)
		self.gpio.write(pin_sr_clk,1)
	self.gpio.write(pin_sr_lat,1)
	self.logger.info("Wrote Bit Pattern")
	
class TestDispatcher(GenericDispatcher):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    def enable_shift_register(self):
        self.logger.info("Enabled Shift Register")
    def disable_shift_register(self):
        self.logger.info("Disabled Shift Register")
    def write_register(self,bit_pattern):
        self.logger.info("Writing Bit Pattern %s", str(bit_pattern))
        # Bit bang the pattern in, top bit first
	bits = list(bit_pattern)
	bits.reverse()
	self.logger.debug("Bit Order %s",str(bits))
	self.logger.info("Wrote Bit Pattern")
