""" Tuner Service. Reads the value of the tuner potentiometer and changes
    the radio station accordingly.

    Using the handle on the left side one can switch between two different
    lists of radio stations or disable radio tuning (leaving only
    remote control with an mpd client).
"""

import logging
import os
import subprocess

import utils

from RPi import GPIO
from options import options

# This is the actual range of the tuner potentiometer
TUNER_RANGE = [0, 800]

# This is is the tolerance of the tuner potentiometer
TUNER_TOLERANCE = 1


class MPG123Source(utils.AudioSource):
    """ Play a playlist using mpg123 (currently not in use) """

    def __init__(self, playlist):
        """ Create an mpg123 player object

            :param playlist: the absolute path of the playlist
                on the filesystem
        """
        self.playlist = playlist

    def cleanup(self):
        """ Stop any other running mpg123 process """
        os.system("killall -9 mpg123")

    def play(self):
        """ Play the playlist """
        self.cleanup()
        subprocess.Popen(["mpg123", "-@", self.playlist])


class MPCSource(utils.AudioSource):
    """ Play a playlist using mpc """

    def __init__(self, playlist):
        """ Create an mpc player object

            :param playlist: the name of the playlist, as known from mpd
        """
        self.playlist = playlist

    def cleanup(self):
        """ Stop playing on the mpd server """
        logging.info("stopping mpc")
        subprocess.call(["mpc", "stop"])

    def play(self):
        """ Play a playlist on the mpd server.

            The method copy the current playlist on the "backup" playlist,
            then empties the current playlist and loads the new playlist.
        """
        logging.info("playing playlist %s on mpc" % self.playlist)

        subprocess.call(["mpc", "rm", "backup"])
        subprocess.call(["mpc", "save", "backup"])
        subprocess.call(["mpc", "clear"])

        subprocess.call(["mpc", "load", self.playlist])
        subprocess.call(["mpc", "play"])


class TunerControl(utils.Service):
    """ Tuner Service """

    name = "Tuner"

    def __init__(self):
        self.playlist_index = 0
        self.playlist = None
        self.tuner = utils.Potentiometer(channel=options.tuner_mcp_channel,
                                         coefficient=0.7)

    def setup(self):
        """ Set up the service. Also start playing a radio station.
        """
        self.read_left_handle()
        if self.radiostations:
            tuner_value = self.read()
            index = self.compute_playlist_index(tuner_value)
            self.change_playlist(index)

    def playlist_range(self, index):
        """Return the tuner range of the given playlist"""
        _min, _max = TUNER_RANGE
        step = (_max - _min) / float(len(self.radiostations))
        return max(_min + index * step, _min),\
            min(_min + (index + 1) * step, _max)

    def compute_playlist_index(self, tuner_value):
        """Return the playlist for the given tuner value"""
        _min, _max = TUNER_RANGE
        N = len(self.radiostations)
        step = (_max - _min) / float(N)

        result = 0
        while (_min + (result+1) * step) < tuner_value:
            result += 1
        return max(min(result, N), 0)

    def change_playlist(self, index):
        logging.info(
            "Tuner: Changing playlist to %s" % index)

        # Change playlist
        self.playlist_index = index
        self.playlist = MPCSource(self.radiostations[self.playlist_index])
        self.playlist.play()

    def read(self):
        return self.tuner.read()

    def read_left_handle(self):
        """
        Read the status of the left handle

        :return: either 0, 1 or 2
        """
        if GPIO.input(options.in_pins["left_1"]) == GPIO.HIGH:
            self.radiostations = options.playlists_1
            return 1
        elif GPIO.input(options.in_pins["left_2"]) == GPIO.HIGH:
            self.radiostations = options.playlists_2
            return 2
        else:
            self.radiostations = None
            return 0

    def loop(self):
        self.read_left_handle()

        if self.radiostations:
            tuner_value = self.read()
            _index = self.compute_playlist_index(tuner_value)

            if _index != self.playlist_index:
                start, end = self.playlist_range(_index)
                if tuner_value >= start + TUNER_TOLERANCE and \
                        tuner_value <= end - TUNER_TOLERANCE:
                    self.change_playlist(_index)

    def stop(self):
        logging.info("Tuner: Shutting down")
        if self.playlist:
            self.playlist.cleanup()


def service():
    return TunerControl()
