"""
This is the main module of Hermann's control code
"""

import logging
import subprocess
import time
import traceback

from RPi import GPIO

from options import options


class Hermann(object):
    """ This is the main class, the services will register to it and it will
        run the main loop
    """
    def __init__(self):
        self.services = []

    def cleanup(self):
        logging.debug("GPIO cleanup")
        try:
            GPIO.cleanup()
        except RuntimeWarning:
            pass

    def _setup_pins(self):
        logging.debug("Setting up pins")
        # setup inputs
        for pin in options.in_pins.values():
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # setup outputs
        for pin in options.out_pins.values():
            GPIO.setup(pin, GPIO.OUT)

    def setup(self):
        """ Setup the application. This includes setting the GPIO pins
            and setting up the services.
        """
        self.cleanup()
        self._setup_pins()

        for service in self.services:
            logging.info("Staring service %s" % service.name)
            service.setup()

        logging.debug("turning leds on")
        GPIO.output(options.out_pins["led"], 1)

        logging.debug("turning amp on")
        GPIO.output(options.out_pins["amp_shutdown"], 1)

    def register_service(self, service):
        """ Register a service. The service will be run inside the main loop.
        """
        self.services.append(service)

    def stop(self):
        """ Stop the application. This includes stopping all the services,
            setting the GPIO pins back to their defaults and disabling
            the audio output of mpd.
        """
        logging.info("stopping the application")
        for service in self.services:
            service.stop()
        subprocess.call(["mpc", "disable", "1"])

        logging.debug("turning leds off")
        GPIO.output(options.out_pins["led"], 0)

        logging.debug("turning amp off")
        GPIO.output(options.out_pins["amp_shutdown"], 0)

    def sleep(self):
        """ Put the application in stand by. This method will be called
            when the on/off switch is turned off.

            It will stop the application and wait for the on/off switch to
            turn on.
        """
        logging.info("Hermann will sleep now")
        self.stop()
        GPIO.setup(options.in_pins["standby"], GPIO.IN,
                   pull_up_down=GPIO.PUD_DOWN)
        GPIO.wait_for_edge(options.in_pins["standby"], GPIO.RISING)
        self.wakeup()

    def wakeup(self):
        """ Wake up from stand by mode. """
        logging.info("Hermann will wake up")
        subprocess.call(["mpc", "enable", "1"])
        self.setup()

    def loop(self):
        """ Execute the main loop of the application """
        if GPIO.input(options.in_pins["standby"]) == GPIO.LOW:
            self.sleep()

        for service in self.services:
            service.loop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # Refer to pins using their board numbers (1-40)
    GPIO.setmode(GPIO.BOARD)

    hermann = Hermann()

    # Read and register services
    for name, args in options.services.items():
        module = __import__(name)
        service = module.service(*args)
        hermann.register_service(service)
    hermann.setup()

    try:
        # Main loop
        while True:
            hermann.loop()
            time.sleep(0.1)
    except Exception as ex:
        # Something bad happened, print it out and safely terminate
        # the application
        traceback.print_exc()
    except BaseException:
        # The application has been terminated (either by Ctrl-C or
        # by shutting down the system).
        # This is ok, just run the cleanup code and terminate.
        pass
    finally:
        hermann.stop()
        hermann.cleanup()
