# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Name:         Xbee Hub
# Purpose:      Code for Xbee hub running via Python Digi Xbee Library (API mode 2)
#
# Author:       james.scouller
#
# Created:      10/02/2022
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# global imports
from digi.xbee.devices import ZigBeeDevice, RemoteZigBeeDevice
from digi.xbee.util import utils
from digi.xbee.models.address import XBee64BitAddress
import threading
from datetime import datetime
import time
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# custom module imports

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# main code

def data_received(xbee_msg):
    received_ts = datetime.fromtimestamp(xbee_msg.timestamp).strftime("%d/%m/%Y %H:%M:%S")
    data = xbee_msg.data.decode().strip('\x00')
    add_64 = xbee_msg.remote_device.get_64bit_addr()
    str_add = utils.hex_to_string(add_64.address).replace(' ', '')
    # check what to do with the kind of message received
    print('{} -> Received {} from {}'.format(received_ts, data, str_add))


serial_port = 'COM3'
baudrate = 115200
dest_add = '0013A20041BB7AFC'
local_xbee = ZigBeeDevice(serial_port, baudrate)
remote_xbee = RemoteZigBeeDevice(local_xbee, XBee64BitAddress.from_hex_string(dest_add))
print('Connecting to local Xbee on {} at {} baud...'.format(serial_port, baudrate))
local_xbee.open()
local_xbee.add_data_received_callback(lambda x: threading.Thread(target=data_received, args=(x,)).start())
print('Connected! Sending message to {}'.format(dest_add))
# local_xbee.send_data_broadcast('Hello XBee World!')
local_xbee.send_data(remote_xbee, 'ON-S1')
local_xbee.send_data(remote_xbee, 'ON-S2')
local_xbee.send_data(remote_xbee, 'ON-S3')
local_xbee.send_data(remote_xbee, 'ON-S4')
time.sleep(10)
local_xbee.send_data(remote_xbee, 'OFF-S1')
local_xbee.send_data(remote_xbee, 'OFF-S2')
local_xbee.send_data(remote_xbee, 'OFF-S3')
local_xbee.send_data(remote_xbee, 'OFF-S4')
time.sleep(10)
print('Terminating connection to Xbee...')
local_xbee.close()
print('Done!')
