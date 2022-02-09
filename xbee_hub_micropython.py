# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Name:         Xbee Hub
# Purpose:      Micropython code for Xbee hub
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


print("Forming a new Zigbee network as a coordinator...")
while network_status() != 0:
    time.sleep(0.1)
print("Network Established\n")

print("Waiting for a remote node to join...")
node_list = []
while len(node_list) == 0:
    # Perform a network discovery until the router joins
    node_list = list(xbee.discover())
print("Remote node found, transmitting data")

node = node_list[0]
dest_addr = node['sender_nwk']  # using 16 bit addressing
dest_node_id = node['node_id']

# Start the ON/OFF loop
print("Starting ON/OFF loop...")
print("Hit CTRL+C to cancel")
while True:
    # turn on
    payload_data = "ON"
    print("Sending \"{}\" to {}".format(payload_data, dest_node_id))
    xbee.transmit(dest_addr, payload_data)
    print('Sleeping for 5 seconds...')
    time.sleep(5)

    # turn off
    payload_data = "OFF"
    print("Sending \"{}\" to {}".format(payload_data, dest_node_id))
    xbee.transmit(dest_addr, payload_data)
    print('Sleeping for 5 seconds...')
    time.sleep(5)
