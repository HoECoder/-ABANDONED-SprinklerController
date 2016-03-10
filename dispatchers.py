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
        self.gpio = pigpio.pi()
        if not self.gpio is None:
            self.__setup_pins()
    def __setup_pins(self):
        self.gpio.set_mode(pin_sr_oe,pigpio.OUTPUT)
	self.gpio.set_mode(pin_sr_clk, pigpio.OUTPUT)
	self.gpio.set_mode(pin_sr_dat, pigpio.OUTPUT)
	self.gpio.set_mode(pin_sr_lat, pigpio.OUTPUT)
	self.gpio.write(pin_sr_noe, 1)
	self.gpio.write(pin_sr_clk, 0)
	self.gpio.write(pin_sr_dat, 0)
	self.gpio.write(pin_sr_lat, 0)
    def __enable_disable_sr(self, bit):
        self.gpio.write(pin_sr_oe,bit)
    def enable_shift_register(self):
        self.__enable_disable_sr(0)
    def disable_shift_register(self):
        self.__enable_disable_sr(1)
    def write_register(self,bit_pattern):
        self.gpio.write(pin_sr_clk,0)
	self.gpio.write(pin_sr_lat,0)
	# Bit bang the pattern in, top bit first
	bits = list(bit_pattern)
	bits.reverse()
	for bit in bits:
		self.gpio.write(pin_sr_clk,0)
		self.gpio.write(pin_sr_dat,bit)
		self.gpio.write(pin_sr_clk,1)
	self.gpio.write(pin_sr_lat,1)
    
	
class TestDispatcher(GenericDispatcher):
    def enable_shift_register(self):
        print "Enable SR"
    def disable_shift_register(self):
        print "Disable SR"
    def write_register(self,bit_pattern):
        # Bit bang the pattern in, top bit first
	bits = list(bit_pattern)
	bits.reverse()
	print "Bang bits: %s" % str(bits)
