# Initialize pyATS by importing this file.
from genie.testbed import load
import os
import json

def restore_mac_assignment(device):
    config_commands = ""
    # Load previously learned MAC address table
    filename = device.hostname + '-macs.txt'
    with open(filename, 'r') as f:
        mac_db = f.read()
        mac_db_json = json.loads(mac_db)
    # Learn information about the new switch
    all_macs = device.parse('show mac address')['mac_table']['vlans']
    show_int_trunk = device.parse('show interface trunk')['interface']
    trunk_int_list = list(show_int_trunk.keys())
    for vlan in all_macs:
        vlan_macs = all_macs[vlan]['mac_addresses']
        for mac in vlan_macs:
            interface = list(vlan_macs[mac]['interfaces'].keys())[0]
            if 'Ethernet' in interface and len(vlan_macs[mac]['interfaces'].keys()) == 1 and interface not in trunk_int_list:
                if mac in list(mac_db_json):
                    print(f"MAC {mac} is on interface {interface} and will be assigned with vlan {mac_db_json[mac]}")
                    config_commands = config_commands + f"interface {interface}\n switchport access vlan {mac_db_json[mac]}\n\n"
                else:
                    print(f"MAC {mac} on interface {interface} was not learned before. Skipping...")
            else:
                print(f"MAC {mac} is not connected to a regular port, skipping...")
    
    print(f"Now we will configure the following settings:\n\n{config_commands}")

    confirm = input("Just making sure we're moving forward with the configuration.. yes or no? ")
    if confirm.lower() == "yes":
        device.configure(config_commands)
    else:
        print("Aborting...")


tb = load('n9k.yaml')
device = tb.devices['SDA-FE1']
device.connect(learn_hostname=True)
restore_mac_assignment(device)

#for device in tb.devices:
#    device.connect()
#    parse_mac_addresses(device)
