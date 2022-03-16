# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Name:         Hub
# Purpose:      Provide interface for Raspberry Pi hub with Xbee radio
#
# Author:       james.scouller
#
# Created:      10/12/2021
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# global imports
import os
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
import time
import serial
import logging
from copy import copy
from datetime import datetime, timedelta
from digi.xbee.exception import InvalidOperatingModeException, TimeoutException, ATCommandException
from digi.xbee.devices import ZigBeeDevice, RemoteZigBeeDevice
from digi.xbee.util import utils
from digi.xbee.models.address import XBee64BitAddress
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# custom module imports
from utils.project import Project
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# main code


class Hub(Project):
    def __init__(self, *args, **kwargs):
        logging.debug('{} __init__ called'.format(__name__))

        # inherit
        Project.__init__(self, *args, **kwargs)

        # setup thread pool executor to handle managing threads associated with Xbee event callbacks
        self.executor = ThreadPoolExecutor(thread_name_prefix='XBcallbacks_ThreadPoolExecutor')

        # setup Xbee device with default 10s timeout
        self.local_xb = ZigBeeDevice(self.CS.port, self.CS.baud)
        self.local_xb.set_sync_ops_timeout(10)

    def connect_xbee(self):
        if self.local_xb and not self.local_xb.is_open():
            connection_attempts = 0
            while connection_attempts < 2 and not self.local_xb.is_open():
                try:
                    self.printF.normalTS("Connecting to Xbee at {0} baud on port: {1}".format(self.CS.baud, self.CS.port))
                    connection_attempts += 1
                    self.local_xb.open()
                    self.local_xb.flush_queues()
                    self.printF.normal('Connected to XBee!')
                    # get the radio address
                    self.hub_address = self.local_xb.get_64bit_addr()
                    self.hub_address_str = utils.hex_to_string(self.hub_address.address).replace(' ', '')
                    # register modem status callback if not already registered (starts in seperate thread so non-blocking)
                    if not self.local_xb._packet_listener.get_modem_status_received_callbacks():
                        self.local_xb.add_modem_status_received_callback(lambda x: self.executor.submit(self.__callback_modem_status, x))
                        self.printF.normal('Setup modem status callback')
                    # register message recieved callback (starts in seperate thread so non-blocking)
                    if not self.local_xb._packet_listener.get_data_received_callbacks():
                        self.local_xb.add_data_received_callback(lambda x: self.executor.submit(self.__callback_data_recieved, x))
                        self.printF.normal('Setup data recieved callback')
                except InvalidOperatingModeException:
                    if connection_attempts < 2:
                        self.printF.normal('Could not determine operating mode. Trying again....')
                    else:
                        self.printF.error('Unable to connect to XBee.')

    def send_message(self, destination, message):
        self.connect_xbee()
        self.printF.normalTS('Sending message to {}:'.format(destination))
        self.printF.indent('{}'.format(message))
        remote_xbee = RemoteZigBeeDevice(self.local_xb, XBee64BitAddress.from_hex_string(destination))
        self.local_xb.send_data(remote_xbee, message)

    def disconnect_xbee(self):
        if self.local_xb and self.local_xb.is_open():
            self.printF.normalTS('Disconnecting Xbee from port: {}'.format(self.CS.port))
            self.local_xb.del_modem_status_received_callback(self.local_xb._packet_listener.get_modem_status_received_callbacks()[0])
            self.printF.normal('Removed modem status callback')
            self.local_xb.del_data_received_callback(self.local_xb._packet_listener.get_data_received_callbacks()[0])
            self.printF.normal('Removed data recieved callback')
            self.local_xb.flush_queues()
            self.printF.normal('Flushed packet queues')
            self.local_xb.close()
            self.printF.normal('Xbee disconnected')

    def __callback_data_recieved(self, xbee_msg):
        """parse received messages"""
        recieved_ts = datetime.fromtimestamp(xbee_msg.timestamp).strftime("%d/%m/%Y %H:%M:%S")
        data = xbee_msg.data.decode().strip('\x00')
        add_64 = xbee_msg.remote_device.get_64bit_addr()
        str_add = utils.hex_to_string(add_64.address).replace(' ', '')
        # print data to screen
        self.printF.normalTS('Message received from {}:'.format(str_add))
        self.printF.indent(data, trim='wrap')
        # do node status once all other expected info recieved
        self.__get_node_status(xbee_msg.remote_device)

    def __callback_modem_status(self, status):
        """display network status"""
        code = utils.hex_to_string(utils.int_to_bytes(status.code, 1))
        logging.debug(status.description)
        self.printF.normalTS(status.description)

    def __get_node_status(self, node):
        """get status info about a remote Xbee radio from supplied remote device instance"""
        # update cached info
        node.read_device_info()

        # create a dict of parameters we are interested in
        node_data = {}
        node_data["ID"] = node.get_node_id()
        node_data["64bit address"] = utils.hex_to_string(node.get_64bit_addr()).replace(' ', '')
        node_data["Status"] = node._get_ai_status().description
        # node_data["Operational sleep time (ms)"] = utils.bytes_to_int(node.get_parameter('OS')) * 10
        # node_data["Operational wake time (ms)"] = utils.bytes_to_int(node.get_parameter('OW'))
        node_data["Temperature (°C)"] = utils.bytes_to_int(node.get_parameter('TP'))
        node_data["Power supply (mV)"] = utils.bytes_to_int(node.get_parameter('%V'))
        node_data["RSSI last packet (dB)"] = utils.bytes_to_int(node.get_parameter('DB'))

        # print to screen
        self.printF.normalTS('Node status report:')
        for (heading, reading) in node_data.items():
            self.printF.indent("{0}: {1}".format(heading, reading))
