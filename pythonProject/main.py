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

# time to send signal to relay for
pulse_s = 0.01
# 2 control pins and 4 relay terminals required per solenoid
# p1-p2 used for reading supply/battery voltages
control_pins = {'D0': None,
                'D1': None,
                'D2': None,
                'D3': None,
                'D4': None,
                'D6': None,
                'D7': None,
                'D8': None}
# register solenoid state as False = Shut = pins pulled LOW
solenoids = {'S1': {'open': False, 'open_pin': 'D0', 'close_pin': 'D1'},
             'S2': {'open': False, 'open_pin': 'D2', 'close_pin': 'D3'},
             'S3': {'open': False, 'open_pin': 'D6', 'close_pin': 'D7'},
             'S4': {'open': False, 'open_pin': 'D4', 'close_pin': 'D8'}}

print(" +--------------------------------------+")
print(" | XBee MicroPython Receive Instruction |")
print(" +--------------------------------------+\n")

def print_pin_status():
    print('Current pin states:')
    for pin_num, p in control_pins.items():
        print('\t{}: {}'.format(pin_num, p.value()))

def print_solenoid_status():
    print('Solenoid states:')
    for num, vars in solenoids.items():
        if vars['open']:
            print('\t{}: open'.format(num))
        else:
            print('\t{}: closed'.format(num))

def network_status():
    # If the value of AI is non zero, the module is not connected to a network
    return xbee.atcmd("AI")

def setup_output_pins(pin_num):
    # configure supplied pin as output
    p = Pin(pin_num, Pin.OUT)
    p.off()
    control_pins[pin_num] = p
    print('Pin {} set as output & LOW'.format(pin_num))

def open_solenoid(num):
    print('Opening solenoid {}...'.format(num))
    # get right pins
    p = control_pins[solenoids[num]['open_pin']]
    # send high signal briefly
    p.on()
    time.sleep(pulse_s)
    p.off()
    # record state
    solenoids[num]['open'] = True
    print('Solenoid {} opened'.format(num))
    print_solenoid_status()

def close_solenoid(num):
    print('Closing solenoid {}...'.format(num))
    # get right pins
    p = control_pins[solenoids[num]['close_pin']]
    # send high signal briefly
    p.on()
    time.sleep(pulse_s)
    p.off()
    # record state
    solenoids[num]['open'] = False
    print('Solenoid {} closed'.format(num))
    print_solenoid_status()

print('Setting up output pins...')
for pin_num in control_pins.keys():
    setup_output_pins(pin_num)
print_pin_status()

print('Joining network as a router...')
while network_status() != 0:
    time.sleep(0.1)
print('Connected to Network\n')

print('Listening...\n')
while True:
    # Check if the XBee has any message in the queue.
    received_msg = xbee.receive()
    if received_msg:
        # Get the sender's 64-bit address and payload from the received message.
        sender = received_msg['sender_eui64']
        sender_str = ''.join('{:02x}'.format(x).upper() for x in sender)
        payload = received_msg['payload']
        msg = payload.decode()
        print('Data received from {} >> {}'.format(sender_str, msg))

        # check for instruction
        if msg[0:4] == 'OFF-':
            num = msg[4::]
            close_solenoid(num)
            response = '{} CLOSED'.format(num)
        elif msg[0:3] == 'ON-':
            num = msg[3::]
            open_solenoid(num)
            response = '{} OPENED'.format(num)
        else:
            response = '"{}" IS NOT A VALID MESSAGE'.format(msg)

        # Send back the same payload to the sender.
        print("Sending back a response...\n")
        xbee.transmit(sender, response)

    # Wait 100 ms before checking for data again.
    time.sleep(0.1)
