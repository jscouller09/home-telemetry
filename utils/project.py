# ----------------------------------------------------------------------------------------------------------------------
# Name:         project
# Purpose:      utility class to read config, setup project directories, generate files, etc.
#
# Author:       James Scouller
#
# Created:      09/06/2020
# ----------------------------------------------------------------------------------------------------------------------
# global imports
import os
import sys
import re
import json
import logging
# ----------------------------------------------------------------------------------------------------------------------
# custom module imports
from utils.config_settings import ConfigSettings
from utils.logger import Logger
from utils.print_wrapper import PrintWrapper
# ----------------------------------------------------------------------------------------------------------------------
# main code


class Project(ConfigSettings):
    def __init__(self, *args, **kwargs):
        logging.debug('{} __init__ called'.format(__name__))

        # inherit
        ConfigSettings.__init__(self, *args, **kwargs)

        # set project name to be supplied name or 'TESTING' by default and create a project directory
        self.proj_name = kwargs['proj_name'] if 'proj_name' in kwargs.keys() else 'TESTING'
        self.proj_name_clean = re.sub(r'\W', '_', self.proj_name)

        # these sub folders need to be made if they don't exist
        self.out_dir = self.__make_folder__(self.cwd, 'output')
        self.proj_dir = self.__make_folder__(self.out_dir, self.proj_name_clean)
        self.log_dir = self.__make_folder__(self.proj_dir, 'logs')
        self.data_dir = self.__make_folder__(self.proj_dir, 'data')

        # update config JSON file path and dump a copy to project dir
        self.update_json_fp(os.path.join(self.proj_dir, 'config_settings.json'))
        self.dump_config()

        # start logger and send all console output to logfile
        self.run_log = Logger(self.log_dir, append=True)
        sys.stdout = self.run_log
        sys.stderr = self.run_log

        # start print wrapper with set max width
        self.printF = PrintWrapper(self.CS.print_width)

        # print header message
        self.printF.header(self.proj_name)
        self.printF.normalTS('Execution began')

    def __make_folder__(self, dir_path, sub_folder):
        logging.debug('{} __make_folder__ called for {}'.format(__name__, sub_folder))
        new_path = os.path.join(dir_path, sub_folder)
        # make the specified folder if it does not exist
        if not os.path.exists(new_path):
            os.makedirs(new_path)
        return new_path


# ----------------------------------------------------------------------------------------------------------------------
# tests

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)-23s (%(threadName)-9s) %(message)s', force=True)

    # set working dir to one level up from current file location by default
    cwd = os.path.split(os.path.dirname(__file__))[0]
    p = Project(cwd=cwd)
