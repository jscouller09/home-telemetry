# ----------------------------------------------------------------------------------------------------------------------
# Name:         Logger
# Purpose:      Provide logging to file support of all console output
#
# Author:       James Scouller
#
# Created:      30/09/2020
# ----------------------------------------------------------------------------------------------------------------------
# global imports
import sys
import os
from datetime import datetime
import logging
# ----------------------------------------------------------------------------------------------------------------------
# custom module imports

# ----------------------------------------------------------------------------------------------------------------------
# main code


class Logger:
    """Logs console output to .log files"""
    def __init__(self, log_dir, append=False, file_name=None, output_widget=None, **kwargs):
        logging.debug('{} __init__ called'.format(__name__))

        # initialise variables
        self.log_dir = log_dir
        self.terminal = sys.stdout
        self.output_widget = output_widget
        self.current_date = ''
        self.log_file_path = ''
        self.append = append
        self.file_name = file_name

        # generate file names
        self.__restart_log_file()

    def write(self, message):
        # re-start log if it is not open
        if self.log.closed:
            self.resume()

        # write to log file
        self.log.write(message)
        # write to console
        self.terminal.write(message)

    def dump(self):
        # use to make sure file is up to date but still open
        self.pause()
        self.resume()

    def pause(self):
        if ~self.log.closed:
            self.log.close()

    def resume(self, text=None):
        # check if we want to start a new logfile (if we are on a new day)
        self.__restart_log_file()
        # if we have text to search for
        if text:
            self.log.close()
            # open log file for reading and writing
            self.log = open(self.log_file_path, '+')

            # read contents of log file until we reach the desired line of text
            searching = True
            contents = ''
            while searching:
                line = self.log.readline()
                contents += line
                if text in line or line is None:
                    searching = False

            # once we've got all the text we want, go back to the beginning of the file
            self.log.seek(0)
            # get rid of any existing data
            self.log.truncate()
            # write the contents we read in
            self.log.write(contents)

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        pass

    # private method to generate filenames and check if they exist or not
    def __check_filename(self, dir_path, suffix, ext='csv'):
        # make filename
        if suffix:
            file_name = '{}_{}.{}'.format(datetime.now().strftime('%Y_%m_%d'), suffix, ext)
        else:
            file_name = '{}.{}'.format(datetime.now().strftime('%Y_%m_%d'), ext)
        # check if we have an existing file
        file_path = os.path.join(dir_path, file_name)
        # return true if file exists, false otherwise
        return os.path.isfile(file_path), file_path

    def __restart_log_file(self):
        # asign file path
        if self.file_name:
            # provided a file name already
            self.log_file_path = os.path.join(self.log_dir, '{}.log'.format(self.file_name))
        elif self.append:
            # no filename, generate and continue to append to existing file
            exists, self.log_file_path = self.__check_filename(self.log_dir, '', 'log')
        else:
            # no filename, generate without appending to existing files
            exists = True
            counter = 0
            while exists:
                exists, self.log_file_path = self.__check_filename(self.log_dir, '{:03d}'.format(counter), 'log')
                if exists:
                    # iterate log file suffix
                    counter += 1

        # open file and append (will be created if it does not exist)
        self.log = open(self.log_file_path, 'a', encoding='utf-8')
