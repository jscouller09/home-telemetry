# ----------------------------------------------------------------------------------------------------------------------
# Name:         hub
# Purpose:      main script for interfacing with Xbee radio setup as hub on Raspberry Pi
#
# Author:       James Scouller
#
# Created:      13/03/2022
# ----------------------------------------------------------------------------------------------------------------------
# global imports
import logging
import os
import sys
import traceback
import signal
import threading
import time
from datetime import datetime
from digi.xbee.devices import ZigBeeDevice, RemoteZigBeeDevice
from digi.xbee.util import utils
from digi.xbee.models.address import XBee64BitAddress
# ----------------------------------------------------------------------------------------------------------------------
# custom module imports
from utils.hub import Hub
# ----------------------------------------------------------------------------------------------------------------------
# main code


def exit_gracefully(*args, **kwargs):
    # callback to make sure a proper system exit is raised if the script is terminated
    if 'hub' in globals():
        hub.printF.header('exiting')
        # disconnect xbee
        hub.disconnect_xbee()
        # close log file
        if hub.run_log:
            hub.printF.normalTS('Stopping run log')
            hub.printF.header()
            hub.run_log.pause()
        else:
            hub.printF.header()
    raise SystemExit()


if __name__ == '__main__':
    try:
        # setup logging level
        logging.basicConfig(level=logging.WARN, format='%(asctime)-23s (%(threadName)-9s) %(message)s', force=True)

        # make sure if the service is stopped/script terminated, it closes ports, logfiles etc.
        signal.signal(signal.SIGINT, exit_gracefully)
        signal.signal(signal.SIGTERM, exit_gracefully)

        # set working dir to one level up from current file location by default
        #cwd = os.path.split(os.path.dirname(__file__))[0]
        cwd = os.path.dirname(__file__)
        hub = Hub(cwd=cwd)

        hub.printF.normalTS('Testing123... looks like it is all working')
        # hub.send_message('0013A20041BB7AFC', 'ON-S1')
        # time.sleep(20)
        # hub.send_message('0013A20041BB7AFC', 'OFF-S1')
        # time.sleep(20)

    except Exception:
        if 'hub' in locals():
            hub.printF.error('Exception occurred in main thread!')
    finally:
        exit_gracefully()
