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
import threading
import time
from datetime import datetime
from digi.xbee.devices import ZigBeeDevice, RemoteZigBeeDevice
from digi.xbee.util import utils
from digi.xbee.models.address import XBee64BitAddress
# ----------------------------------------------------------------------------------------------------------------------
# custom module imports
from utils.project import Project
# ----------------------------------------------------------------------------------------------------------------------
# main code


def main(*args, **kwargs):
    try:
        p = Project(*args, **kwargs)

        p.printF.normalTS('Testing123... looks like it is all working')
    except Exception:
        if 'p' in locals():
            p.printF.error('Exception in main thread occured!')
        # comment out if you want to suppress additional trace below error report
        traceback.print_exc(file=sys.stdout)
    finally:
        if 'p' in locals() and p.run_log:
            p.printF.header('exiting')
            p.printF.normal()
            # close log file
            p.printF.header()
            p.run_log.pause()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)-23s (%(threadName)-9s) %(message)s', force=True)

    # set working dir to one level up from current file location by default
    cwd = os.path.split(os.path.dirname(__file__))[0]
    main(cwd=cwd)
