# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Name:         Xbee Node
# Purpose:      Micropython code for Xbee node
#
# Author:       james.scouller
#
# Created:      06/02/2022
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# global imports
import xbee
import time
from machine import Pin
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# custom module imports

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# main code


def network_status():
    # If the value of AI is non zero, the module is not connected to a network
    return xbee.atcmd("AI")


def format_eui64(addr):
    return ':'.join('%02x' % b for b in addr)


def format_packet(p):
    type = 'Broadcast' if p['broadcast'] else 'Unicast'
    print("%s message from EUI-64 %s (network 0x%04X)" % (type, format_eui64(p['sender_eui64']), p['sender_nwk']))
    print(" from EP 0x%02X to EP 0x%02X, Cluster 0x%04X, Profile 0x%04X:" % (p['source_ep'], p['dest_ep'], p['cluster'], p['profile']))
    print(p['payload'])
    return p['payload'].decode('utf-8')


print("Joining network as a router...")
while network_status() != 0:
    time.sleep(0.1)
print("Connected to Network\n")

# configure AD1 as an output pin
d1 = Pin.board.D1
d1.mode(Pin.OUT)
d1.on()
print('D1 set as output & HIGH. Listening for packets...')

# listen for packets
while True:
    p = xbee.receive()
    if p:
        payload = format_packet(p)
        if payload == 'ON':
            # turn on switch by pulling low
            print('Got ON command! Pulling D1 LOW')
            d1.off()
        elif payload == 'OFF':
            # turn off switch by pulling high
            print('Got OFF command! Pulling D1 HIGH')
            d1.on()
    time.sleep(0.25)

    # print('Test off - pulling D1 high')
    # d1.on()
    # print('Sleeping 5s...')
    # time.sleep(5)
    # print('Test on - pulling D1 low')
    # d1.off()
    # print('Sleeping 5s...')
    # time.sleep(5)
