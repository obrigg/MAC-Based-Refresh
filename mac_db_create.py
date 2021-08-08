# Initialize pyATS by importing this file.
from genie.testbed import load
import json

def parse_mac_addresses(device):
    mac_db = {}
    all_macs = device.parse('show mac address')['mac_table']['vlans']
    # Save parsed data for backup, just in case.
    filename = device.hostname + '-original.txt'
    with open(filename, 'w') as f:
        f.write(str(all_macs))
    # Sort the information from the switch
    show_int_trunk = device.parse('show interface trunk')['interface']
    trunk_int_list = list(show_int_trunk.keys())
    for vlan in all_macs:
        vlan_macs = all_macs[vlan]['mac_addresses']
        for mac in vlan_macs:
            interface = list(vlan_macs[mac]['interfaces'].keys())[0]
            if 'Ethernet' in interface and len(vlan_macs[mac]['interfaces'].keys()) == 1 and interface not in trunk_int_list:
                mac_db[mac] = vlan
                print(f"MAC {mac} is on vlan {vlan}")
            else:
                print(f"MAC {mac} is not connected to an access port, skipping...")
    # Save results to file
    filename = device.hostname + '-macs.txt'
    with open(filename, 'w') as f:
        f.write(json.dumps(mac_db))

tb = load('n9k.yaml')
device = tb.devices['SDA-FE1']
device.connect(learn_hostname=True)
parse_mac_addresses(device)

#for device in tb.devices:
#    device.connect()
#    parse_mac_addresses(device)
