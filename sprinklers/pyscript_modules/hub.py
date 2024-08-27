import logging
from digi.xbee.devices import ZigBeeDevice, RemoteZigBeeDevice
from digi.xbee.util import utils
from digi.xbee.models.address import XBee64BitAddress
from datetime import datetime
import time
import threading
import re

# setup logging
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# setup local xbee radio
serial_port = '/dev/ttyUSB0'
baudrate = 115200
local_xbee = ZigBeeDevice(serial_port, baudrate)
waiter_reply = threading.Event()
expected_reply = None
supply_v = ''
temp = ''
pres = ''
hum = ''
reply = ''


def send_message(dest_add, msg, await_reply=None):
    logger.debug('sending {} to {}'.format(msg, dest_add))
    connect_xb()
    remote_xbee = RemoteZigBeeDevice(local_xbee, XBee64BitAddress.from_hex_string(dest_add))
    waiter_reply.clear()
    if await_reply is not None:
        global expected_reply
        expected_reply = '{}:{}'.format(dest_add, await_reply)
    local_xbee.send_data(remote_xbee, msg)
    if await_reply is not None and waiter_reply.wait(20):
        logger.debug('got expected reply {}'.format(await_reply))
    elif await_reply is not None:
        logger.debug('timed out after 20s waiting for reply {}'.format(await_reply))
    else:
        logger.debug('waited 20s to ensure message went through')
    disconnect_xb()
    global supply_v
    global temp
    global pres
    global hum
    global reply
    return supply_v, temp, pres, hum, reply


def __data_received(xbee_msg):
    received_ts = datetime.fromtimestamp(xbee_msg.timestamp).strftime("%d/%m/%Y %H:%M:%S")
    data = xbee_msg.data.decode().strip('\x00')
    add_64 = xbee_msg.remote_device.get_64bit_addr()
    str_add = utils.hex_to_string(add_64.address).replace(' ', '')

    # check who message was from and the contents
    if expected_reply and (expected_reply in '{}:{}'.format(str_add, data)):
        # let waiting thread know we got the correct reply
        waiter_reply.set()
        # extract supply voltage measurement if present
        match = re.search('SUPPLY: (-?\d{1,2}.\d{3})V', data)
        if match:
            global supply_v
            supply_v = match.group(1)
        # extract other measurements if present
        match = re.search('TEMP: (-?\d{1,2}.\d{1,2})°C', data)
        if match:
            global temp
            temp = match.group(1)
        match = re.search('PRESSURE: (-?\d{1,3}.\d{1,3})kPa', data)
        if match:
            global pres
            pres = match.group(1)
        match = re.search('HUMIDITY: (-?\d{1,3}.\d{1,2})%', data)
        if match:
            global hum
            hum = match.group(1)
    logger.debug('{} -> received {} from {}'.format(received_ts, data, str_add))
    global reply
    reply = data


def connect_xb():
    if local_xbee and not local_xbee.is_open():
        logger.debug('connecting to local Xbee on {} at {} baud...'.format(serial_port, baudrate))
        local_xbee.open()
        local_xbee.add_data_received_callback(lambda x: threading.Thread(target=__data_received, args=(x,)).start())
        logger.debug('connected to local xbee')


def disconnect_xb():
    if local_xbee and local_xbee.is_open():
        logger.debug('terminating connection to local xbee...')
        local_xbee.del_data_received_callback(local_xbee._packet_listener.get_data_received_callbacks()[0])
        local_xbee.close()
        logger.debug('connection to local xbee closed')
