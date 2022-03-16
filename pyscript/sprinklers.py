import logging
import sys

# setup logging
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

if "/config/pyscript_modules" not in sys.path:
    sys.path.append("/config/pyscript_modules")
logger.debug(sys.path)

import hub

# register state trigger for sprinkers
@state_trigger("input_boolean.sprinkler_1== 'on'")
@state_trigger("input_boolean.sprinkler_1== 'off'")
@state_trigger("input_boolean.sprinkler_2== 'on'")
@state_trigger("input_boolean.sprinkler_2== 'off'")
@state_trigger("input_boolean.sprinkler_3== 'on'")
@state_trigger("input_boolean.sprinkler_3== 'off'")
@state_trigger("input_boolean.sprinkler_4== 'on'")
@state_trigger("input_boolean.sprinkler_4== 'off'")
def toggle_sprinkler(**kwargs):
    # pick right destination radion and solenoid valve based on config
    logger.debug('toggle_sprinkler called with kwargs: {}'.format(kwargs))
    if 'sprinkler_1' in kwargs['var_name']:
        radio_address = '0013A20041BB7AFC'
        solenoid = 'S1'
    elif 'sprinkler_2' in kwargs['var_name']:
        radio_address = '0013A20041BB7AFC'
        solenoid = 'S2'
    elif 'sprinkler_3' in kwargs['var_name']:
        radio_address = '0013A20041BB7AFC'
        solenoid = 'S3'
    elif 'sprinkler_4' in kwargs['var_name']:
        radio_address = '0013A20041BB7AFC'
        solenoid = 'S4'
    else:
        logger.debug('could not determine which sprinkler and radio address to use!')
        radio_address = False
        solenoid = False
    # determine message to send and expected reply
    if kwargs['value'] == 'off' and kwargs['old_value'] == 'on':
        # turn off
        state = 'OFF'
        reply = 'CLOSED'
    elif kwargs['value'] == 'on' and kwargs['old_value'] == 'off':
        # turn on
        state = 'ON'
        reply = 'OPENED'
    else:
        logger.debug('could not determine which state and reply to use!')
        state = False
        reply = False
    if all([radio_address, solenoid, state, reply]):
        # setup asyncronous task to connect to the local xbee hub, send the message, await the reply and then disconnect
        task.executor(hub.send_message, radio_address, '{}-{}'.format(state, solenoid), '{} {}'.format(solenoid, reply))
