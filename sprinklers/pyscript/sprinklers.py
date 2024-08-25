import logging
import sys
from datetime import datetime, timedelta

# setup logging
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

if "/config/pyscript_modules" not in sys.path:
    sys.path.append("/config/pyscript_modules")
logger.debug(sys.path)

import hub

# setup state vars
sprinkler_names = ['sprinkler_1', 'sprinkler_2', 'sprinkler_3', 'sprinkler_4', 'sprinkler_5']
state.set('pyscript.{}'.format(sprinkler_names[0]), 'off', supply_v=0.0, temp=0.0, pres=0.0, hum=0.0, solenoid='S1', radio_address='0013A20041BB7AFC', last_off=None, last_on=None)
state.set('pyscript.{}'.format(sprinkler_names[1]), 'off', supply_v=0.0, temp=0.0, pres=0.0, hum=0.0, solenoid='S2', radio_address='0013A20041BB7AFC', last_off=None, last_on=None)
state.set('pyscript.{}'.format(sprinkler_names[2]), 'off', supply_v=0.0, temp=0.0, pres=0.0, hum=0.0, solenoid='S3', radio_address='0013A20041BB7AFC', last_off=None, last_on=None)
state.set('pyscript.{}'.format(sprinkler_names[3]), 'off', supply_v=0.0, temp=0.0, pres=0.0, hum=0.0, solenoid='S4', radio_address='0013A20041BB7AFC', last_off=None, last_on=None)
state.set('pyscript.{}'.format(sprinkler_names[4]), 'off', supply_v=0.0, temp=0.0, pres=0.0, hum=0.0, solenoid='S1', radio_address='0013A20041B9EB71', last_off=None, last_on=None)


# register state trigger for sprinkers
@state_trigger("input_boolean.sprinkler_1== 'on'")
@state_trigger("input_boolean.sprinkler_1== 'off'")
@state_trigger("input_boolean.sprinkler_2== 'on'")
@state_trigger("input_boolean.sprinkler_2== 'off'")
@state_trigger("input_boolean.sprinkler_3== 'on'")
@state_trigger("input_boolean.sprinkler_3== 'off'")
@state_trigger("input_boolean.sprinkler_4== 'on'")
@state_trigger("input_boolean.sprinkler_4== 'off'")
@state_trigger("input_boolean.sprinkler_5== 'on'")
@state_trigger("input_boolean.sprinkler_5== 'off'")
def toggle_sprinkler(*args, **kwargs):
    # pick right destination radion and solenoid valve based on config
    logger.debug('toggle_sprinkler called with ags: {}'.format(args))
    logger.debug('toggle_sprinkler called with kwargs: {}'.format(kwargs))
    state_var_name = "pyscript.{}".format(kwargs['var_name'].split('.')[1])
    state_var = state.get(state_var_name)
    if 'sprinkler_' in kwargs['var_name']:
        radio_address = state_var.radio_address
        solenoid = state_var.solenoid
    else:
        logger.debug('could not determine which sprinkler and radio address to use!')
        radio_address = False
        solenoid = False
    # determine message to send and expected reply
    if kwargs['value'] == 'off' and kwargs['old_value'] == 'on':
        # turn off
        status = 'OFF'
        reply = 'CLOSED'
    elif kwargs['value'] == 'on' and kwargs['old_value'] == 'off':
        # turn on
        status = 'ON'
        reply = 'OPENED'
    else:
        logger.debug('could not determine which status and reply to use!')
        status = False
        reply = False
    if all([radio_address, solenoid, status, reply]):
        # setup asyncronous task to connect to the local xbee hub, send the message, await the reply and then disconnect
        supply_v, temp, pres, hum, full_reply = task.executor(hub.send_message, radio_address, '{}-{}'.format(status, solenoid), '{} {}'.format(solenoid, reply))
        logger.debug('response was: {}'.format(full_reply))
        logger.debug('supply V reported was: {}'.format(supply_v))
        logger.debug('temperature reported was: {}'.format(temp))
        logger.debug('pressure reported was: {}'.format(pres))
        logger.debug('humidity reported was: {}'.format(hum))
        if supply_v and supply_v != '':
            state_var.supply_v = float(supply_v)
        if temp and temp != '':
            state_var.temp = float(temp)
        if pres and pres != '':
            state_var.pres = float(pres)
        if hum and hum != '':
            state_var.hum = float(hum)
        if status == 'ON':
            state_var.last_on=state.get(kwargs['var_name']).last_changed
            # update state variable
            state.set(state_var_name, state.get(kwargs['var_name']), supply_v=state_var.supply_v, temp=state_var.temp, pres=state_var.pres, hum=state_var.hum, solenoid=state_var.solenoid, radio_address=state_var.radio_address, last_off=state_var.last_off, last_on=state_var.last_on)
            # setup asycronous task to send an off signal after the specified time
            num_mins = int(float(input_number.sprinkler_timer))
            send_time = datetime.now() + timedelta(minutes=num_mins)
            logger.debug('delaying turn off for {} minutes until {:%Y/%m/%d %H:%M:%S}'.format(num_mins, send_time))
            trig_info = task.wait_until(
                    state_trigger="{} == 'off'".format(kwargs['var_name']),
                    timeout=60.0 * float(input_number.sprinkler_timer)
                )
            if trig_info["trigger_type"] == "timeout":
                # timeout elapsed without the solenoid being shut off manually
                state.set(kwargs['var_name'], 'off')
        else:
            state_var.last_off=state.get(kwargs['var_name']).last_changed
            # update state variable
            state.set(state_var_name, state.get(kwargs['var_name']), supply_v=state_var.supply_v, temp=state_var.temp, pres=state_var.pres, hum=state_var.hum, solenoid=state_var.solenoid, radio_address=state_var.radio_address, last_off=state_var.last_off, last_on=state_var.last_on)

@service
def update_sprinkler_measurements(*args, **kwargs):
    # pick right destination radio and solenoid valve based on config
    logger.debug('update_sprinkler_measurements called with ags: {}'.format(args))
    logger.debug('update_sprinkler_measurements called with kwargs: {}'.format(kwargs))
    state_var_name = "pyscript.{}".format(kwargs['var_name'].split('.')[1])
    state_var = state.get(state_var_name)
    radio_address = state_var.radio_address
    # setup asyncronous task to connect to the local xbee hub, send the message, await the reply and then disconnect
    supply_v, temp, pres, hum, full_reply = task.executor(hub.send_message, radio_address, 'MEASURE', 'SUPPLY:')
    logger.debug('response was: {}'.format(full_reply))
    logger.debug('supply V reported was: {}'.format(supply_v))
    logger.debug('temperature reported was: {}'.format(temp))
    logger.debug('pressure reported was: {}'.format(pres))
    logger.debug('humidity reported was: {}'.format(hum))
    if supply_v and supply_v != '':
        state_var.supply_v = float(supply_v)
    if temp and temp != '':
        state_var.temp = float(temp)
    if pres and pres != '':
        state_var.pres = float(pres)
    if hum and hum != '':
        state_var.hum = float(hum)
    # update state variable
    state.set(state_var_name, state.get(kwargs['var_name']), supply_v=state_var.supply_v, temp=state_var.temp, pres=state_var.pres, hum=state_var.hum, solenoid=state_var.solenoid, radio_address=state_var.radio_address, last_off=state_var.last_off, last_on=state_var.last_on)
