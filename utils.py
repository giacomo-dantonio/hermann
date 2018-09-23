""" Different utilities
"""

import spidev


class MCP3008(object):
    """ Communicate with the MPC3008. This code has been taken from the book
        "Raspberry Pi: Einstieg - Optimierung - Projekte" from Maik Schmidt.
    """
    def __init__(self, bus=0, client=0):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, client)
        self.spi.max_speed_hz = 500000


    def analog_read(self, channel):
        if (channel < 0 or channel > 7):
            return -1
        result = self.spi.xfer2([1, (8 + channel) << 4, 0])
        return ((result[1] & 3) << 8) + result[2]

mcp = MCP3008()


class Potentiometer(object):
    """ Class to read the value of a potentiometer. Since Hermann's tuning
        potentiometer gives back very unstable values, we need some averaging
        method. An averaging coefficient can be set in the constructor.
    """
    def __init__(self, channel, coefficient=1):
        """ Create an object to read the value of a potentiometer through
            the MCP3008.

            :param channel: The channel on the MPC3008 to read from.
            :type channel: int

            :param coefficient: The averaging coefficient, this is optional.
                The default value 1 means that no averaging will be made.
            :type averaging: int
        """
        self.channel = channel
        self.coefficient = coefficient
        self.value = 0
        self.last_read = 0

    def read(self):
        """ Read the (average) value of the potentiometer.

            The value is also set to self.value.
            The read value without averaging is set to self.last_read.

            :return: an integer value between 0 and 1024
        """
        self.last_read = mcp.analog_read(self.channel)
        self.value = (1-self.coefficient) * self.value + \
            self.coefficient * self.last_read
        return self.value


class AudioSource(object):
    """ Basis class for "player" objects.
    """
    def __init__(self):
        pass

    def cleanup(self):
        pass

    def play(self):
        pass


class Service(object):
    """ Basis class for services """
    name = ""
    pins = []

    def setup(self):
        pass

    def loop(self):
        pass

    def stop(self):
        pass
