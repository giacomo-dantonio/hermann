""" Volume service. Reads the value of the volume potentiometer and
    sets the volume of the analog audio output accordingly.
"""

import alsaaudio
import math

import utils

from options import options


class VolumePoti(utils.Service):
    name = "Volume"

    def read_volume(self):
        # correct the read value because the potentiometer is not logarithmic
        value = math.log(self.poti.read())

        # convert the value to a volume level accepted by alsaaudio
        return int((value/math.log(1023.0)) * 100)

    def setup(self):
        self.mixer = alsaaudio.Mixer("PCM")
        self.poti = utils.Potentiometer(options.volume_mcp_channel)

    def loop(self):
        value = self.read_volume()
        if value != self.mixer.getvolume()[0]:
            self.mixer.setvolume(value)


def service():
    return VolumePoti()
