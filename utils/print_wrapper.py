# ----------------------------------------------------------------------------------------------------------------------
# Name:         PrintWrapper
# Purpose:      Provide pretty-print formatting for console logging/output
#
# Author:       James Scouller & Ben Throssell
#
# Created:      30/09/2020
# ----------------------------------------------------------------------------------------------------------------------
# global imports
from datetime import datetime
import traceback
import sys
import logging
# ----------------------------------------------------------------------------------------------------------------------
# custom module imports

# ----------------------------------------------------------------------------------------------------------------------
# main code


class PrintWrapper:
    """Wraps and formats console output using custom template"""
    def __init__(self, max_width=80, **kwargs):
        logging.debug('{} __init__ called'.format(__name__))

        self.max_width = max_width
        self.lenTs = 19

    def process_special_characters(func):
        # allow for processing of special characters such as \r
        def inner(self, msg='', msg_prefix='', trim='right', **kwargs):
            # constructing kwargs argument
            # if there is a \r in the message then we want to preserve this
            if str(msg)[:1] == '\r':
                msg_prefix = msg[:1]
                msg = msg[1:]
            return func(self, msg, trim, msg_prefix, **kwargs)
        return inner

    @process_special_characters
    def header(self, msg='', trim='right', msg_prefix='', **kwargs):
        msg = self.__trim(msg, st_len=self.max_width - 2, trim=trim)
        print("+{0:{fill}{align}{width}s}+".format(msg.upper(), msg_prefix=msg_prefix, fill='-', align='^', width=self.max_width - 2), **kwargs)

    @process_special_characters
    def normalTS(self, msg='', trim='right', msg_prefix='', **kwargs):
        t = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        msg = self.__trim(msg, st_len=self.max_width - self.lenTs - 6, trim=trim)
        print("{msg_prefix}| {0:{ts_width}} > {1:{fill}{align}{width}s}|".format(t, msg, msg_prefix=msg_prefix, fill=' ', align='<', width=(self.max_width - self.lenTs - 6), ts_width=self.lenTs), **kwargs)

    @process_special_characters
    def normal(self, msg='', trim='right', msg_prefix='', **kwargs):
        msg = self.__trim(msg, st_len=self.max_width - self.lenTs - 6, trim=trim)
        print("{msg_prefix}| {0:{ts_width}}{1:{fill}{align}{width}s}|".format('', msg, msg_prefix=msg_prefix, fill=' ', align='<', width=self.max_width - self.lenTs - 6, ts_width=self.lenTs + 3), **kwargs)

    @process_special_characters
    def indent(self, msg='', trim='right', msg_prefix='', **kwargs):
        msg = self.__trim(msg, st_len=self.max_width - self.lenTs - 8, trim=trim)
        print("{msg_prefix}| {0:{ts_width}}{1:{fill}{align}{width}s}|".format('', msg, msg_prefix=msg_prefix, fill=' ', align='<', width=self.max_width - self.lenTs - 8, ts_width=self.lenTs + 5), **kwargs)

    def error(self, msg):
        print()
        self.header('ERROR REPORT')
        # print("\n+{0:{fill}{align}{width}s}+".format('ERROR REPORT', fill='-', align='^', width=self.max_width - 2))
        print("| {0:{fill}{align}{width}s}|".format(msg, fill=' ', align='<', width=self.max_width - 3))
        print("|{0:{fill}{align}{width}s}|".format('', fill=' ', align='<', width=self.max_width - 2))

        # get exception info and split out components for nice printing
        exc_type, exc_value, exc_traceback = sys.exc_info()
        trace = traceback.format_exception(exc_type, exc_value, exc_traceback)
        calls = trace[1:-1]
        message_body = "{0}\n".format(msg)

        # go through and print list of calls (starting from first one which is last on list)
        for i, call in enumerate(calls[::-1]):
            file = call.split(',')[0].replace('"', '')[7::]
            line = call.split(',')[1].strip()
            funcParts = call.split(',')[2::]
            func = ''.join(funcParts).split('\n')[1].strip()
            message_body += "Call {0} -> {1}\n".format(i, file)
            message_body += "       -> {0}: {1}\n".format(line, func)
            # shortening if required
            fileS = self.__shorten_left(file, self.max_width - 12)
            funcS = self.__shorten_left(func, self.max_width - 12 - len(line) - 2)
            place = "{0}: {1}".format(line, funcS)
            print("| Call {0} ->{1: <{width}s}|".format(i, fileS, width=self.max_width - 12))
            print("|        ->{0: <{width}s}|".format(place, width=self.max_width - 12))
            print("|{0:{fill}{align}{width}s}|".format('', fill=' ', align='<', width=self.max_width - 2))

        # get final error message and shorten if required
        err = trace[-1].strip()
        message_body += " {0}\n".format(err)
        errS = self.__shorten_left(err, self.max_width - 5)
        print("| {0:{fill}{align}{width}s}|".format(errS, fill=' ', align='<', width=self.max_width - 3))
        print("+{0:{fill}{align}{width}s}+".format('', fill='-', align='^', width=self.max_width - 2))
        raise SystemExit()

    @process_special_characters
    def warn(self, msg='', trim='right', msg_prefix='', **kwargs):
        t = 'WARNING!'
        msg = self.__trim(msg, st_len=self.max_width - self.lenTs - 6, trim=trim)
        print("{msg_prefix}| {0:{ts_width}} > {1:{fill}{align}{width}s}|".format(t, msg, msg_prefix=msg_prefix, fill=' ', align='<', width=(self.max_width - self.lenTs - 6), ts_width=self.lenTs), **kwargs)

        # print("{msg_prefix}| WARNING! > {0:{fill}{align}{width}s}|".format(msg, msg_prefix=msg_prefix, fill=' ', align='<', width=self.max_width - 6), **kwargs)

    def __trim(self, msg, st_len, trim='right'):
        if trim == 'right':
            msg = self.__shorten_right(str(msg), st_len)
        elif trim == 'left':
            msg = self.__shorten_left(str(msg), st_len)
        elif trim == 'wrap':
            this_msg = msg[:st_len] + '|'
            msg = msg[st_len:]
            while msg != '':
                m = msg[:st_len - 2]
                # m_1 = self.__trim(m, st_len=self.max_width - self.lenTs - 8, trim='left')
                m_2 = "| {0:{ts_width}}{1:{fill}{align}{width}s}|".format('', m, fill=' ', align='<', width=self.max_width - self.lenTs - 8, ts_width=self.lenTs + 5)
                this_msg += '\n' + m_2
                msg = msg[st_len - 2:]

            msg = this_msg[:-1]
        else:
            raise KeyError(f'trim option "{trim}" does not exist, use "right", "left" or "wrap"')
            msg = msg
        return msg

    def __shorten_left(self, s, maxLen):
        curLen = len(s)
        if len(s) > maxLen:
            # shorten string by truncating the start
            st = curLen - maxLen + 3
            return "...{0}".format(s[st::])
        else:
            return s

    def __shorten_right(self, s, maxLen):
        if len(s) > maxLen:
            # shorten string by truncating the end
            ed = maxLen - 3
            return "{0}...".format(s[0:ed])
        else:
            return s


# ----------------------------------------------------------------------------------------------------------------------
# tests

if __name__ == '__main__':
    printF = PrintWrapper()
    # printF.warn('watch out')
    printF.header('testing print types')
    printF.normal('normal')
    printF.normalTS('normalTS')
    printF.indent('indent')
    printF.warn('warn')

    msg = ''
    printF.header('Testing trim')
    for i in range(50):
        msg += f'str{i}'
    printF.normal(msg)
    printF.normalTS(msg)
    printF.indent(msg)
    printF.warn(msg)

    printF.header('Testing line wrapping')
    printF.normal(msg, trim='wrap')
    printF.normalTS(msg, trim='wrap')
    printF.indent(msg, trim='wrap')
    printF.warn(msg, trim='wrap')

    printF.header('Testing in place printing')
    kwargs = {'end': ""}
    # for i in range(10):
    #     # end = ""
    #     sleep(.5)
    #     printF.normal(f'\rhi {i}',**kwargs)
    print('')
    printF.normal('Testing in place printing')
