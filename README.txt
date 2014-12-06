Hermann is an old tube radio (a Lorenz Säntis 52K) which I modified
to function as an internet radio.

It runs arch linux on a Raspberry Pi. Music Player Daemon takes care
of playing audio.

This is the python code which runs the controls.

Hermann has the following controls:

- A volume potentiometer, whose value is read from a ADC (MCP3008 from Adafruit)
  and used to set the volume of the Raspberry Pi.

- Another potentiometer connected with the radio tuner. Its value is also read
  from the ADC and use to select a radio station.

- An on/off switch. Its value is read from the GPIO interface of the Pi and
  used to put the radio in "stand by" (meaning that the mpd server is stopped,
  its output is disabled, the GPIO pins are reset and the audio amplifier
  is shut down).

- A couple of LEDs which light the tuner panel, connected to the GPIO interface
  of the Pi.

- A mono class D audio amplifier from Adafruit. Its power and shutdown pins are
  connected to the GPIOs of the Pi, its audio input is connected to the analog
  audio output of the pi. Its audio output is connected directly to the old
  speaker of the Säntis.

To run the code, just run the module hermann.py. The code should be run as root.
For example:

    # python -m hermann