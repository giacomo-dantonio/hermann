"""
This module contains the configuration of hermann.
"""

from RPi import GPIO


class Options(object):  # FIXME: read from filesystem
    def __init__(self):
        # Channels on the MCP3008
        self.volume_mcp_channel = 0
        self.tuner_mcp_channel = 1
#        # radio station playlists to be used with mpg123
#         self.playlists = [
#             "playlists/ndrkultur.m3u",  # NDR Kultur
#             "playlists/funkhaus-europa.m3u",  # Funkhaus Europa
#             "playlists/dkultur.m3u",  # Deutschlandradio Kultur
#             "playlists/nordwestradio.m3u",  # Nordwestradio
#             "playlists/bremenvier.m3u",  # Bremen 4
#             "playlists/bremeneins.m3u",  # Bremen 1
#         ]

        # radio station playlists to be used with mpd
        # One can switch between the two lists using
        # the handle on the left side
        self.playlists_1 = [
            "ndrkultur",  # NDR Kultur
            "funkhaus-europa",  # Funkhaus Europa
            "dkultur",  # Deutschlandradio Kultur
            "nordwestradio",  # Nordwestradio
            "bremenvier",  # Bremen 4
            "bremeneins",  # Bremen 1
        ]
        # The two playlists are for the moment the same,
        self.playlists_2 = self.playlists_1

        # active services
        # the keys are the service names and have to correspond to a python
        # module (e.g. tuner.py for tuner).
        # the values are constructor parameters
        self.services = {
            "tuner": [],
            "volume": [],
        }

        # Input pins, they will all be set up as input pins
        # with software pull down resistors
        self.in_pins = {
            "standby": 36,
            "left_1": 40,
            "left_2": 38,
        }

        # Output pins
        self.out_pins = {
            "amp_shutdown": 8,
            "led": 16,
        }


options = Options()
