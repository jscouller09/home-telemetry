# ----------------------------------------------------------------------------------------------------------------------
# Name:         initial_config
# Purpose:      setup initial configuration settings for use with config_settings class
#
# Author:       James Scouller
#
# Created:      13/03/2022
# ----------------------------------------------------------------------------------------------------------------------
# global imports
import logging
# ----------------------------------------------------------------------------------------------------------------------
# custom module imports

# ----------------------------------------------------------------------------------------------------------------------
# main code


class InitialConfig:
    logging.debug('{} called'.format(__name__))

    # set maximum print width for log files and console
    print_width = 97

    # set baud rate for all Xbee radios to match radio configuration
    # this will also be used as the baud rate for all serial communication
    baud = 115200

    # set COM port to use for serial communication with xbee radios
    port = 'COM3'
