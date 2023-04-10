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
from machine import Pin, ADC
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# custom module imports

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# main code

# note latching valves seem to require different voltages (usually lower than expected e.g. -6V to -7V for a 9V solenoid) to turn off properly
# time to send signal to relay for
pulse_s = 10#0.05 # depends on the solenoid valve, usually 0.05-0.1s is fine if the voltage is set right
# the following dictionary gives the function of each of the configurable Xbee pins
xbee_pins = {'D0': None,
             'D1': 'SCL',
             'D2': 'V_BATT',
             'D3': 'MP_S0',
             'D4': 'MP_S3',
             'D5': 'XB_ASSOC',
             'D6': 'MP_S1',
             'D7': 'MP_S2',
             'D8': 'MP_COM',
             'D9': None,
             'P0': 'XB_RSSI',
             'P1': 'SDA',
             'P2': 'MP_EN',
             'P3': None,
             'P4': None,
             }
# control pins
control_pins = {
    'MP_S0': None,
    'MP_S1': None,
    'MP_S2': None,
    'MP_S3': None,
    'MP_COM': None,
    'MP_EN': None,
}
vin_pins = {'V_BATT': ADC('D2')}
# truth table
truth_table = {
    'S5_ON': {
        'MP_S0': 'HIGH',
        'MP_S1': 'LOW',
        'MP_S2': 'LOW',
        'MP_S3': 'LOW'
    },
    'S5_OFF': {
        'MP_S0': 'LOW',
        'MP_S1': 'HIGH',
        'MP_S2': 'LOW',
        'MP_S3': 'LOW'
    },
    'S4_ON': {
        'MP_S0': 'HIGH',
        'MP_S1': 'HIGH',
        'MP_S2': 'LOW',
        'MP_S3': 'LOW'
    },
    'S4_OFF': {
        'MP_S0': 'LOW',
        'MP_S1': 'LOW',
        'MP_S2': 'HIGH',
        'MP_S3': 'LOW'
    },
    'S1_OFF': {
        'MP_S0': 'HIGH',
        'MP_S1': 'LOW',
        'MP_S2': 'HIGH',
        'MP_S3': 'LOW'
    },
    'S3_ON': {
        'MP_S0': 'LOW',
        'MP_S1': 'HIGH',
        'MP_S2': 'HIGH',
        'MP_S3': 'LOW'
    },
    'S3_OFF': {
        'MP_S0': 'HIGH',
        'MP_S1': 'HIGH',
        'MP_S2': 'HIGH',
        'MP_S3': 'LOW'
    },
    'S2_OFF': {
        'MP_S0': 'LOW',
        'MP_S1': 'LOW',
        'MP_S2': 'LOW',
        'MP_S3': 'HIGH'
    },
    'S2_ON': {
        'MP_S0': 'HIGH',
        'MP_S1': 'LOW',
        'MP_S2': 'LOW',
        'MP_S3': 'HIGH'
    },
    'S1_ON': {
        'MP_S0': 'LOW',
        'MP_S1': 'HIGH',
        'MP_S2': 'LOW',
        'MP_S3': 'HIGH'
    },
}

# register solenoid state as False = Shut
# MP control pins are high by default
solenoids = {'S1': False,
             'S2': False,
             'S3': False,
             'S4': False,
             'S5': False,
             }

print(" +--------------------------------------+")
print(" | XBee MicroPython Receive Instruction |")
print(" +--------------------------------------+\n")

def setup_output_pins():
    print('Setting up output pins to default HIGH...')
    for pin_num, sig_name in xbee_pins.items():
        if sig_name in control_pins.keys():
            # configure supplied pin as output
            p = Pin(pin_num, Pin.OUT)
            p.on()
            control_pins[sig_name] = p
            print('\tPin {} = {}'.format(pin_num, sig_name))

def print_pin_status():
    print('Current pin states:')
    for sig_name, p in control_pins.items():
        print('\t{}: {}'.format(sig_name, p.value()))
    for sig_name, p in vin_pins.items():
        print('\t{}: {} V'.format(sig_name, get_supply_voltage(scale=False, display=False)))

def get_supply_voltage(scale=True, display=True):
    raw_mV = vin_pins['V_BATT'].read_u16() * 1250 / 65535
    if scale:
        supply_v = (raw_mV / 1000.0) * (1500.0 + 200.0) / 200.0
    else:
        supply_v = (raw_mV / 1000.0)
    if display:
        print('SUPPLY: {:02.3f} V'.format(supply_v))
    return supply_v

def print_solenoid_status():
    print('Solenoid states:')
    for num, state in solenoids.items():
        if state:
            print('\t{}: open'.format(num))
        else:
            print('\t{}: closed'.format(num))

def network_status():
    # If the value of AI is non zero, the module is not connected to a network
    return xbee.atcmd("AI")

def toggle_solenoid(num, open=False):
    # get right sequence from the truth table to select the right channel of the multiplexer
    if open:
        print('Opening solenoid {}...'.format(num))
        sequence = truth_table[num + '_ON']
    else:
        print('Closing solenoid {}...'.format(num))
        sequence = truth_table[num + '_OFF']
    for sig_name, state in sequence.items():
        if state == 'HIGH':
            control_pins[sig_name].on()
        elif state == 'LOW':
            control_pins[sig_name].off()
    # now enable the multiplexer by pulling low
    control_pins['MP_EN'].off()
    # send low signal briefly
    control_pins['MP_COM'].off()
    time.sleep(pulse_s)
    control_pins['MP_COM'].on()
    # disable multiplexer by pulling high
    control_pins['MP_EN'].on()
    # record state
    if open:
        solenoids[num] = True
        print('Solenoid {} opened'.format(num))
    else:
        solenoids[num] = False
        print('Solenoid {} closed'.format(num))
    print_solenoid_status()

# setup output pins
setup_output_pins()
# show states
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
            toggle_solenoid(num, open=False)
            response = '{} CLOSED. SUPPLY: {:02.3f}V'.format(num, get_supply_voltage())
        elif msg[0:3] == 'ON-':
            num = msg[3::]
            toggle_solenoid(num, open=True)
            response = '{} OPENED. SUPPLY: {:02.3f}V'.format(num, get_supply_voltage())
        elif msg[0:6] == 'SUPPLY':
            response = 'SUPPLY: {:02.3f}V'.format(get_supply_voltage())
        else:
            response = '"{}" IS NOT A VALID MESSAGE'.format(msg)

        # Send back the same payload to the sender.
        print("Sending back a response...\n")
        print(response)
        xbee.transmit(sender, response)

    # Wait 100 ms before checking for data again.
    time.sleep(0.1)
