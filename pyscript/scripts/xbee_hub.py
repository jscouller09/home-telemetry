# ----------------------------------------------------------------------------------------------------------------------
# Name:         Xbee Hub
# Purpose:      
#
# Author:       james.scouller
#
# Created:      
# ----------------------------------------------------------------------------------------------------------------------
# global imports
from digi.xbee.devices import ZigBeeDevice, RemoteZigBeeDevice
from digi.xbee.util import utils
from digi.xbee.models.address import XBee64BitAddress
import threading
from datetime import datetime
import logging
# ----------------------------------------------------------------------------------------------------------------------
# custom module imports

# ----------------------------------------------------------------------------------------------------------------------
# main code


logging.basicConfig(level=logging.DEBUG, format='%(asctime)-23s (%(threadName)-9s) %(message)s', force=True)


def data_received(xbee_msg):
    received_ts = datetime.fromtimestamp(xbee_msg.timestamp).strftime("%d/%m/%Y %H:%M:%S")
    data = xbee_msg.data.decode().strip('\x00')
    add_64 = xbee_msg.remote_device.get_64bit_addr()
    str_add = utils.hex_to_string(add_64.address).replace(' ', '')
    # check what to do with the kind of message received
    logging.debug('{} -> Received {} from {}'.format(received_ts, data, str_add))

def connect_xb():
    logging.debug('Connecting to local Xbee on {} at {} baud...'.format(serial_port, baudrate))
    local_xb.open()
    local_xb.add_data_received_callback(lambda x: threading.Thread(target=data_received, args=(x,)).start())
    logging.debug('Connected!')

def disconnect_xb():
    logging.debug('Terminating connection to Xbee...')
    local_xb.del_data_received_callback(local_xb._packet_listener.get_data_received_callbacks()[0])
    local_xb.flush_queues()
    local_xb.close()
    logging.debug('Done!')

def send_data(destination, msg):
    remote_xbee = RemoteZigBeeDevice(local_xb, XBee64BitAddress.from_hex_string(destination))
    local_xb.send_data(remote_xbee, msg)

serial_port = 'COM3'
baudrate = 115200
local_xb = ZigBeeDevice(serial_port, baudrate)
dest_add = '0013A20041BB7AFC'
# send_data(dest_add, 'ON-S1')
# send_data(dest_add, 'OFF-S1')


@state_trigger("input_boolean.test_sprinkler== 'on'")
@state_trigger("input_boolean.test_sprinkler== 'off'")
def toggle_sprinkler(**kwargs):
    log.info(f"toggle_sprinkler called with kwargs={kwargs}")
    # if kwargs['value'] == 'on':
    #     send_data(dest_add, 'ON-S1')
    # elif kwargs['value'] == 'off':
    #     send_data(dest_add, 'OFF-S1')