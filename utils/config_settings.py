# ----------------------------------------------------------------------------------------------------------------------
# Name:         config_settings
# Purpose:      provide class to setup configuration settings and interface with JSON configuration file
#
# Author:       James Scouller
#
# Created:      13/03/2022
# ----------------------------------------------------------------------------------------------------------------------
# global imports
import os
import json
import logging
# ----------------------------------------------------------------------------------------------------------------------
# custom module imports
from utils.initial_config import InitialConfig as CS
# ----------------------------------------------------------------------------------------------------------------------
# main code


class ConfigSettings:
    def __init__(self, *args, **kwargs):
        logging.debug('{} __init__ called'.format(__name__))

        # set working dir to one level up from current file location by default
        self.cwd = kwargs['cwd'] if 'cwd' in kwargs.keys() else os.path.split(os.path.dirname(__file__))[0]
        # set json file path to a file called config_settings.json in the working dir by default
        self.json_fp = kwargs['cwd'] if 'json_fp' in kwargs.keys() else os.path.join(self.cwd, 'config_settings.json')
        self.CS = CS
        # attempt to load configuration settings from an existing JSON file
        self.load_config()

    def update_json_fp(self, new_json_fp):
        logging.debug('{} update_json_fp called'.format(__name__))
        # update the stored JSON file path to the new supplied one
        self.json_fp = new_json_fp

    def load_config(self):
        logging.debug('{} load_config called'.format(__name__))
        # read config settings from JSON file and assign them as attributes of CS
        # if the file does not exist, the initial config settings are left in place
        if os.path.isfile(self.json_fp):
            logging.debug('found \'{}\' file'.format(os.path.basename(self.json_fp)))
            with open(self.json_fp, 'r') as file:
                self.__parse_config_dict__(json.load(file))
        else:
            logging.debug('no config file found')
            logging.debug('settings from initial_config remain')

    def dump_config(self):
        logging.debug('{} dump_config called'.format(__name__))
        # dump config settings to JSON file
        with open(self.json_fp, 'w') as file:
            config_dict = dict([(key, val) for (key, val) in self.CS.__dict__.items() if '__' not in key])
            json.dump(config_dict, file, indent=4)
            logging.debug('wrote config settings to {}'.format(os.path.basename(self.json_fp)))

    def __parse_config_dict__(self, config_dict):
        logging.debug('{} __parse_config_dict__ called'.format(__name__))
        # assign dictionary attributes to the class
        config_dict = dict([(key, val) for (key, val) in config_dict.items() if '__' not in key])
        for key in config_dict:
            setattr(self.CS, key, config_dict[key])
