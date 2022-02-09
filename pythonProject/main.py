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
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# custom module imports

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# main code


print(" +--------------------------------------+")
print(" | XBee MicroPython Receive Data Sample |")
print(" +--------------------------------------+\n")

def network_status():
    # If the value of AI is non zero, the module is not connected to a network
    return xbee.atcmd("AI")

print("Joining network as a router...")
while network_status() != 0:
    time.sleep(0.1)
print("Connected to Network\n")

print("Waiting for data...\n")
while True:
    # Check if the XBee has any message in the queue.
    received_msg = xbee.receive()
    if received_msg:
        # Get the sender's 64-bit address and payload from the received message.
        sender = received_msg['sender_eui64']
        payload = received_msg['payload']
        print("Data received from %s >> %s" % (''.join('{:02x}'.format(x).upper() for x in sender),
                                               payload.decode()))

        # Send back the same payload to the sender.
        print("Sending back a response...\n")
        xbee.transmit(sender, payload)

    # Wait 100 ms before checking for data again.
    time.sleep(0.1)
